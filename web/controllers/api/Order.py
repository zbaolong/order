import decimal
import json

from flask import request, g, jsonify

from common.libs.UrlManager import UrlManager
from common.libs.member.CartService import CartService
from common.libs.pay.PayService import PayService
from common.models.food.food import Food
from web.controllers.api import route_api
from common.libs.pay.PayService import PayService


@route_api.route("/order/info", methods=["POST"])
def order_info():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None
    member_info = g.member_info
    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads(params_goods)

    food_dic = {}
    for item in params_goods_list:
        food_dic[item['id']] = item['number']

    food_ids = food_dic.keys()
    food_list = Food.query.filter(Food.id.in_(food_ids)).all()
    data_food_list = []
    yun_price = pay_price = decimal.Decimal(0.00)
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': item.name,
                'price': str(item.price),
                'pic_url': UrlManager.build_image_url(item.main_image),
                'number': food_dic[item.id]
            }
            pay_price = pay_price + item.price * int(food_dic[item.id])
            data_food_list.append(tmp_data)
    # 获取地址
    default_address = {
        "name":"编程浪子",
        "mobile": "17282728228",
        "address":"上海虹桥"
    }
    resp['data']['food_list'] = data_food_list
    resp['data']['pay_price'] = str(pay_price)
    resp['data']['yun_price'] = str(yun_price)
    resp['data']['total_price'] = str(pay_price + yun_price)
    resp['data']['default_address'] = default_address
    return jsonify(resp)


@route_api.route("/order/create", methods=['POST'])
def order_create():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    type = req['type'] if 'type' in req else ''
    note = req['note'] if 'note' in req else ''
    express_address_id = int(req['express_address_id']) if 'express_address_id' in req and req['express_address_id'] else 0
    params_goods = req['goods'] if 'goods' in req else None

    items = []
    if params_goods:
        items = json.loads(params_goods)

    if len(items) < 1:
        resp['code'] = -1
        resp['msg'] = '下单失败：没有选择商品~~'
        return jsonify(resp)
    member_info = g.member_info

    target = PayService()
    params = {}
    resp = target.create_order(member_info.id, items, params)
    if resp['code'] == 200 and type == "cart":
        CartService.delete_item(member_info.id, items)
    return jsonify(resp)
