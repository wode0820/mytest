import requests
import traceback
import base64
import hashlib
import calendar
import datetime
import uuid
import time
import json
# from utile import aes

TEST_HOST = "http://backend-game-debug.huixuanjiasu.com"
ONLINE_HOST = "http://bump.kcrgkj.cn"
pkg_name = "com.huixuan.luckyfruit"

class ContentTest:

    def __init__(self, yid, version_name, channel_name, game_version, device_id, is_test, game_count):
        self.yid = yid
        assert "_" in yid
        self.user_id = yid.split("_")[0]
        self.version_name = version_name
        self.channel_name = channel_name
        self.device_id = device_id
        self.game_version = game_version
        self.is_test = is_test
        if self.is_test:
            self.host = TEST_HOST
        else:
            self.host = ONLINE_HOST
        self.count = game_count
        self.is_video = 0
        # self.aes = aes.AESTool(aes_iv="0000000000000000", app_secret="ad_config_199201")

    def get_question(self):
        url = f"{self.host}/luck_fruit/game/hc_fruit"
        params = dict(
            version_name=self.version_name,
            game_version=self.game_version,
            channel_name=self.channel_name,
            user_id=self.user_id,
            yid=self.yid,
            device_id=self.device_id,
            box_pkg_name=pkg_name
        )
        cookies = dict(
            yid=self.yid,
            device_id=self.device_id,
            android_id=self.device_id
        )

        dt = '{"is_xg": 0, "combo": ["2"], "game_time": 6}'
        body = dict(business_data=dt)
        sign_data = self.get_sign(channel_name=self.channel_name,
                                  version_name=self.version_name,
                                  uri='/luck_fruit/game/hc_fruit',
                                  device_id=self.device_id)
        params.update(sign_data)
        try:
            resp = requests.request(method="POST", url=url, params=params, data=body, cookies=cookies)
            resp = resp.json()
            # print(resp)
            if resp.get("ecp"):  # 解密
                resp = json.loads(self.aes.decrypt(resp["data"]))
            print(resp)

            data = resp["data"]
            xg_count = data["xg_count"]
            red_data = data["red_data"]
            if red_data.get('type'):
                type = red_data.get('type')
                if int(type) == 3:
                    print("------------------------------------------------------")
                    print("f没有奖励")
                    # print(f"当前用户 {self.user_id},已合成{xg_count}个西瓜,{red_data}")
                    time.sleep(1)
                    self.get_hc_record()
                elif int(type) == 2:
                    print("------------------------------------------------------")
                    self.is_video = 1
                    print(f"当前用户 {self.user_id},已合成{xg_count}个西瓜,{red_data}")
                    self.get_hc_record()
                    self.is_video = 0




        except Exception:
            traceback.print_exc()

    def get_hc_record(self):
        url = f"{self.host}/luck_fruit/behaviors/get_hc_record"
        params = dict(
            version_name=self.version_name,
            channel_name=self.channel_name,
            game_version=self.game_version,
            yid=self.yid,
            user_id=self.user_id,
            device_id=self.device_id,
            oaid='37fefbfb-ff7f-5bf7-7f7f-d72fd6d7cb50',
            ii='ODY1MTI2MDQwMjkxMjc3',
            box_pkg_name=pkg_name
        )
        cookies = dict(
            yid=self.yid,
            device_id=self.device_id,
            android_id=self.device_id
        )

        body = dict(is_video=self.is_video)
        sign_data = self.get_sign(channel_name=self.channel_name,
                                  version_name=self.version_name,
                                  uri='/luck_fruit/behaviors/get_hc_record',
                                  device_id=self.device_id)
        params.update(sign_data)
        try:
            resp = requests.request(method="POST", url=url, params=params, data=body, cookies=cookies)
            resp = resp.json()
            if resp.get("ecp"):   # 解密
                pass
                resp = json.loads(self.aes.decrypt(resp["data"]))
            data = resp["data"]
            reward = data["reward"]
            cash_balance = data["cash_balance"]
            print(f"本次获得红包:{reward/1000} , 用户余额为:{cash_balance/1000}")
            time.sleep(0.5)
        except Exception:
            traceback.print_exc()

    def get_sign(self, uri, version_name, channel_name, device_id):
        sign_data = {}
        secret = "gohell"
        nonce_str = uuid.uuid1()
        future = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        expiry = calendar.timegm(future.timetuple())
        secure_link = f"{uri} {version_name} {channel_name} {device_id} {expiry} {nonce_str} {secret}".encode('utf-8')
        hash = hashlib.md5(secure_link).digest()
        base64_hash = base64.urlsafe_b64encode(hash)
        str_hash = base64_hash.decode('utf-8').rstrip('=')
        sign_data["sign"] = str_hash
        sign_data["nonce_str"] = nonce_str
        sign_data["et"] = expiry
        return sign_data

    @classmethod
    def get_code_music_id(cls, code):
        id_hex = code.split('L')[0]
        return str(int(id_hex.upper(), 16))

    def start_test(self):
        for i in range(self.count):
            self.get_question()
            time.sleep(0.5)


if __name__ == '__main__':
    """测试配置"""
    #yid = "35644161_5306548961"  # 抓包yid
    yid = "13150891_1300286178"    # ceshi
    game_count = 30
    is_test = 1   # 0线上  1测试
    version_name = "1.1.2.0"
    channel_name = "google"
    game_version = '1.0.2.6'   # ceshi
    # game_version = '1.0.1.6'
    # channel_name = "toutiao"    # xianshang
    # device_id = "fd27ee77-f2d5-3a6a-a503-f351b139f4f9"  # ab   xianshang
    device_id = "6fcd5672-9723-33af-9b83-b9f9711fa8b2"  # ab
    # 年龄端上调
    """"""

    test = ContentTest(yid=yid,
                       game_count=game_count,
                       is_test=is_test,
                       channel_name=channel_name,
                       version_name=version_name,
                       device_id=device_id,
                       game_version=game_version)
    test.start_test()
