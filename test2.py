import json
import urllib.request

from alicebot.plugin import Plugin

# 各种变量
caiyunapp_token = "填写你自己的Token"
location = '110.33119,20.031971' #海南海口市辖区
req_rain = 'https://api.caiyunapp.com/v2.6/%s/%s/minutely' % (caiyunapp_token, location)
req_info = 'https://api.caiyunapp.com/v2.6/%s/%s/realtime' % (caiyunapp_token, location)
json_rain_response = urllib.request.urlopen(req_rain).read()
json_info_response = urllib.request.urlopen(req_info).read()
json_rain = json.loads(json_rain_response)
json_info = json.loads(json_info_response)
err = "仅支持查询海口市市辖区内如下内容\n- 信息：今日天气\n- 预警：天气预警\n- 降雨：市辖区内降雨信息（后期再做可自选精确到区...太菜了还不会）\n用法：天气[空格]你要查询的项目"
sky_dict = {"CLEAR_DAY":"晴",
                        "CLEAR_NIGHT":"晴",
                        "PARTLY_CLOUDY_DAY":"多云",
                        "PARTLY_CLOUDY_NIGHT":"多云",
                        "CLOUDY":"阴",
                        "LIGHT_HAZE":"轻度雾霾",
                        "MODERATE_HAZE":"中度雾霾",
                        "HEAVY_HAZE":"重度雾霾",
                        "LIGHT_RAIN": "小雨",
                        "MODERATE_RAIN": "中雨",
                        "HEAVY_RAIN": "大雨",
                        "STORM_RAIN":"暴雨",
                        "FOG":"雾"} # 创建天气字典，海口没有雪也没浮尘天气就不加了

class CycoFirstPlugin(Plugin):
    async def handle(self) -> None:
        w_type = self.event.get_plain_text().split(" ")
        if len(w_type) == 2:
            await self.event.reply(await self.get_weather_info(w_type[1]))
        else:
            await self.event.reply(err)

    async def rule(self) -> bool:
        if self.event.adapter.name != "cqhttp":
            return False
        if self.event.type != "message":
            return False
        return self.event.message.startswith("天气")

    @staticmethod
    async def get_weather_info(typ):
        if typ not in ["信息", "降雨", "预警"]:
            return err
        elif typ == "信息":
            if json_info.get('status') == 'ok':
                rain = json_rain.get('result').get('minutely').get('description')
                skycon = json_info.get('result').get('realtime').get('skycon')
                skycon_result = sky_dict[skycon]
                temp = str(json_info.get('result').get('realtime').get('temperature'))
                humidity = str(float(json_info.get('result').get('realtime').get('humidity')) * 100)
                air_level = json_info.get('result').get('realtime').get('air_quality').get("description").get('usa')
                uv = json_info.get('result').get('realtime').get('life_index').get("ultraviolet").get("desc")
                return "海口市市辖区---今日天气\n" + skycon_result + " " + temp + "℃\n湿度 " + humidity + "\n紫外线强度 " + uv + "\n空气质量 " + air_level + "\n" + rain
        elif typ == "降雨":
            if json_rain.get('status') == 'ok':
                rain = json_rain.get('result').get('minutely').get('description')
                return "海口市市辖区---降雨预报\n" + rain
            else:
                return "连接到服务出错，请检查配置"
