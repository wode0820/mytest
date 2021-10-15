import requests
import traceback
import base64
import hashlib
import calendar
import datetime
import uuid
import time, json
from utile import setting
from utile import aes

TEST_HOST = "http://backend-game-debug.huixuanjiasu.com/juice"
ONLINE_HOST = "http://wldzk.yuanlijuzhen.com"
pkg_name = "com.wdxk.pourjuice"


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
        self.aes = aes.AESTool(aes_iv="0000000000000000", app_secret="ad_config_199201")
        self.level = 1

    def start_game(self):
        url = f"{self.host}/game/start_game"
        params = dict(
            version_name=self.version_name,
            game_version=self.game_version,
            channel_name=self.channel_name,
            user_id=self.user_id,
            device_id=self.device_id,
            oaid='47FC4B40F5254F1C97A77E48E1A1DAB84f28677e544ce5bfc0553cc41e29dab6',
            ii='ODYyNTY2MDQ1ODc0NTMx',
            box_pkg_name=pkg_name
        )
        cookies = dict(
            yid=self.yid,
            device_id=self.device_id,
            android_id=self.device_id
        )
        body = dict(
            yid=self.yid,
            device_id=self.device_id,
            business_data=json.dumps({"is_forbid":'null'})
        )
        sign_data = self.get_sign(channel_name=self.channel_name,
                                  version_name=self.version_name,
                                  uri='/game/start_game',
                                  device_id=self.device_id)
        params.update(sign_data)
        try:
            resp = requests.request(method="POST", url=url, params=params, data=body, cookies=cookies)
            resp = resp.json()
            if resp.get("ecp"):   # 解密
                resp = json.loads(self.aes.decrypt(resp["data"]))
            content_id = resp["data"]['question_info']['content_id']
            # cash_balance = data['cash_balance']
            # if len(str(int(cash_balance))) >= 4:
            #     cash_balance = cash_balance / 10000
            #     cash_balance = f"{cash_balance} 元 "
            # game_balance = data['game_balance']
            # print(f"{self.user_id} 用户本次获得红包 {cash_balance}; 金币 {game_balance}")
            self.level = content_id
            self.get_reward()
        except Exception:
            traceback.print_exc()

    def get_reward(self):
        url = f"{self.host}/game/submit_answer"
        params = dict(
            version_name=self.version_name,
            game_version=self.game_version,
            channel_name=self.channel_name,
            user_id=self.user_id,
            device_id=self.device_id,
            oaid='47FC4B40F5254F1C97A77E48E1A1DAB84f28677e544ce5bfc0553cc41e29dab6',
            ii='ODYyNTY2MDQ1ODc0NTMx',
            box_pkg_name=pkg_name
        )
        cookies = dict(
            yid=self.yid,
            device_id=self.device_id,
            android_id=self.device_id
        )
        da = {"game_time":0,"total_game_count": self.level,"is_hard":False,"is_relive":0,"is_tg":0,
              "content_id":self.level,"local_used_time":0,"agreement_time":0}
        body = dict(
            yid=self.yid,
            device_id=self.device_id,
            business_data=json.dumps(da)
        )
        sign_data = self.get_sign(channel_name=self.channel_name,
                                  version_name=self.version_name,
                                  uri='/game/submit_answer',
                                  device_id=self.device_id)
        params.update(sign_data)
        try:
            resp = requests.request(method="POST", url=url, params=params, data=body, cookies=cookies)
            resp = resp.json()
            if resp.get("ecp"):   # 解密
                resp = json.loads(self.aes.decrypt(resp["data"]))
            data = resp["data"]['reward']
            # cash_balance = data['cash_balance']
            # if len(str(int(cash_balance))) >= 4:
            #     cash_balance = cash_balance / 10000
            #     cash_balance = f"{cash_balance} 元 "
            # game_balance = data['game_balance']
            print(f"{self.user_id} 用户本次获得红包 {data} 元")
            # print('-------------------------------------------------')
            self.sync_quest()
        except Exception:
            traceback.print_exc()

    def sync_quest(self):
        url = f"{self.host}/game/tg_ad_reward"
        params = dict(
            version_name=self.version_name,
            game_version=self.game_version,
            channel_name=self.channel_name,
            user_id=self.user_id,
            device_id=self.device_id,
            oaid='47FC4B40F5254F1C97A77E48E1A1DAB84f28677e544ce5bfc0553cc41e29dab6',
            ii='/game/sync_guest',
            box_pkg_name=pkg_name
        )
        cookies = dict(
            yid=self.yid,
            device_id=self.device_id,
            android_id=self.device_id
        )
        body = dict(
            yid=self.yid,
            device_id=self.device_id,
        )
        sign_data = self.get_sign(channel_name=self.channel_name,
                                  version_name=self.version_name,
                                  uri='/game/tg_ad_reward',
                                  device_id=self.device_id)
        params.update(sign_data)
        try:
            resp = requests.request(method="POST", url=url, params=params, data=body, cookies=cookies)
            resp = resp.json()
            if resp.get("ecp"):  # 解密
                resp = json.loads(self.aes.decrypt(resp["data"]))
            data = resp["data"]['reward']
            # guest_total = data['guest_total']
            # level = data['level']
            print(f"{self.user_id} 用户翻倍获取奖励 {data} 元")
            print('-------------------------------------------------')
        except Exception:
            traceback.print_exc()

    def info(self):
        pass

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
            self.start_game()
            time.sleep(0.1)


if __name__ == '__main__':
    """测试配置"""
    yid = "11887761_3945748958"  # 抓包yid
    game_count = 100
    is_test = 1   # 0线上  1测试
    version_name = "1.0.1.9"
    channel_name = "oppo"
    # game_version = '1.0.7.8'
    game_version = '1.0.1.9'
    # channel_name = "vivo"
    device_id = "e4d94211-a2d1-34cf-86ed-a63087d2d5b2"  # ab
    # device_id = "574e555e-0226-379c-b850-dad9b752d925"  # ab
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
