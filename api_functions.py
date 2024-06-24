import requests
import json
import math

import os
from dotenv import load_dotenv
load_dotenv()

# Env. variables
DEBUG_MODE = os.environ.get("DEBUG_MODE")
NVR_KEY_ID = os.environ.get("NVR_KEY_ID")
NVR_KEY_SECRET = os.environ.get("NVR_KEY_SECRET")
DATA_GO_ENC = os.environ.get("DATA_GO_ENC")
DATA_GO_DEC = os.environ.get("DATA_GO_DEC")


latlon_coeff = 111.70107212763709 # = 6400 * 2 * math.pi / 360



# 즐겨찾기 장소의 쿠키 처리를 위한 문자열-dict 변환
def cookieString2DictObj(cookie_string):
    if cookie_string==None:
        return None
    return  json.loads(cookie_string)

def dictObj2CookieString(dict_obj):
    if dict_obj==None:
        return None
    return  json.dumps(dict_obj)


# 위경도 두 지점의 근사적 거리를 계산 (정확한 계산을 목적으로 하지 않음.)
def getSquaredDistance(lat0, lon0, lat1, lon1):
    # 경도 1도의 거리는 lat0의 위도를 기준으로 함.
    long_dist_per_degree = math.cos(lat0) * latlon_coeff

    dLong = long_dist_per_degree * abs(lon0 - lon1)
    dLatt = latlon_coeff * abs(lat0 - lat1)
    squared_dist = dLong * dLong + dLatt * dLatt
    
    return squared_dist

   

def getAPI(strLat, strLon):
    url = 'https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc'
    
    # 좌표계는 기본값(위경도), 변환 작업 이름 불필요, 
    params ={
        'coords' : (strLon + ',' + strLat), 
        'output' : 'json'
    }
    
    # 헤더의 API 인증정보 
    headers = {
  	    "X-NCP-APIGW-API-KEY-ID": NVR_KEY_ID,
	    "X-NCP-APIGW-API-KEY" : NVR_KEY_SECRET    
    }
    
    response = requests.get(url, params=params, headers=headers)
    result_json_string = response.content.decode("utf-8")
    result_json_obj = json.loads(result_json_string)
    
    #print(result_json_obj)
    city_name = result_json_obj['results'][0]['region']['area1']['name']

    if DEBUG_MODE:
        print(city_name)
        
    # 지자체별 API 분기
    if city_name == '서울특별시':
        return 'API_SEOUL'
        
    return 'API_TAGO'   


def getClosestBustopSeoul(strLat, strLon):
    url = 'http://ws.bus.go.kr/api/rest/stationinfo/getStationByPos'
    params ={
        'serviceKey' : DATA_GO_DEC, 
        'tmX' : strLon,
        'tmY' : strLat,
        'radius' : '500',
        'resultType' : 'json'
    }

    response = requests.get(url, params=params)
    result_json_string = response.content.decode("utf-8")
    result_json_obj = json.loads(result_json_string)
    near_stops = result_json_obj['msgBody']['itemList']
    
    if near_stops == None:
        return None

    closest_stop = None
    min_dist = 100

    for stop in near_stops:
        if int(stop['dist']) < min_dist:
            closest_stop = stop
            min_dist = int(stop['dist'])
    return closest_stop


# 서울을 제외한 지역의 인접 정류소
def getClosestBustop(strLat, strLon):
    url = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCrdntPrxmtSttnList'
    params ={
        'serviceKey' : DATA_GO_DEC, 
        'numOfRows' : 50,
        'gpsLong' : strLon,
        'gpsLati' : strLat,
        '_type' : 'json'
    }
   
    response = requests.get(url, params=params)
    result_json_string = response.content.decode("utf-8")
    result_json_obj = json.loads(result_json_string)
    
    print(result_json_obj)
    
    near_stops = result_json_obj['response']['body']['items']['item']
    
    if DEBUG_MODE:
        print(near_stops)
        
    if near_stops == None:
        return None        

    closest_stop = None
    min_dist = 1000000
    
    here_lat = float(strLat)
    here_lon = float(strLon)

    for stop in near_stops:
        stop_distance = getSquaredDistance(here_lat, here_lon, stop['gpslati'], stop['gpslong'])
        if stop_distance < min_dist:
            closest_stop = stop
            min_dist = stop_distance
            print(min_dist)
            
    return closest_stop

# 특정 정류장의 도착시간 정보 조회
def getBusArrivalInfoSeoul(station_id, bust_stop_id):
    url = 'http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid'
    params ={
        'serviceKey' : DATA_GO_DEC, 
        'arsId' : bust_stop_id,
        'resultType' : 'json'
    }

    response = requests.get(url, params=params)
    result_json_string = response.content.decode("utf-8")
    result_json_obj = json.loads(result_json_string)
    bus_infos = result_json_obj['msgBody']['itemList']

    summary = {}
    for bus in bus_infos:
        
        if bus["stId"]!=station_id or bus["arsId"]!=bust_stop_id:
            continue
        
        # 기존에 있던 번호인지 확인
        if bus["busRouteAbrv"] in summary:
            if summary[bus["busRouteAbrv"]] > bus["arrmsg1"]:
                summary[bus["busRouteAbrv"]] = bus["arrmsg1"]            
        else:
           summary[bus["busRouteAbrv"]] =  bus["arrmsg1"]

    return summary


# 특정 정류장의 도착시간 정보 조회
def getBusArrivalInfo(cityCode, nodeId):
    url = 'http://apis.data.go.kr/1613000/ArvlInfoInqireService/getSttnAcctoArvlPrearngeInfoList'
    
    params ={
        'serviceKey' : DATA_GO_DEC, 
        'numOfRows' : 10,
        'cityCode' : cityCode,
        'nodeId' : nodeId,
        '_type' : 'json'
    }

    response = requests.get(url, params=params)
    result_json_string = response.content.decode("utf-8")
    result_json_obj = json.loads(result_json_string)
    
    bus_infos = result_json_obj['response']['body']['items']['item']
    
    
    summary = {}
    # 노선별 가장 빨리 도착하는 정보만 사용
    for bus in bus_infos:
        # 기존에 있던 번호인지 확인
        if bus["routeno"] in summary:
            if summary[bus["routeno"]] > bus["arrtime"]:
                summary[bus["routeno"]] = bus["arrtime"]            
        else:
           summary[bus["routeno"]] =  bus["arrtime"]

    return summary



def getNextBuses(strLat, strLon):
    
    result = {
        "lat" : strLat,
        "lon" : strLon
    }
    
    API = getAPI(strLat, strLon)    
    result['API'] = API
    
    if API=='API_SEOUL':
        cloest_bus_stop = getClosestBustopSeoul(strLat, strLon)
        if cloest_bus_stop == None:
            print('There is no stop around here in Seoul.')
            result["result"] = "NG"
            result["error_msg"] = "주변 500m에 정류소가 없어요."

        else:
            result["result"] = "OK"
            #print(cloest_bus_stop)
            strNearLon = cloest_bus_stop['gpsX']
            strNearLat = cloest_bus_stop['gpsY']
            
            print("최근접 정류소 위도 : " + strNearLat )
            print("최근접 정류소 경도 : " + strNearLon )
        
            # 식별 된 버스 정류장의 도착 정보
            print("정류장 이름 - " + cloest_bus_stop['stationNm']) 
            
            result["near_stop"] = {
                "API" : API,
                "lat" : strNearLat,
                "lon" : strNearLon,
                "name" : cloest_bus_stop['stationNm'],
                "q_param_1" : cloest_bus_stop['stationId'],
                "q_param_2" : cloest_bus_stop['arsId']
            }
            
            info = getBusArrivalInfoSeoul(cloest_bus_stop['stationId'], cloest_bus_stop['arsId'])
            result["next_buses"] = info
            
    else:
        cloest_bus_stop = getClosestBustop(strLat, strLon)
        
        if cloest_bus_stop == None:
            print('There is no stop around here.')
            result["result"] = "NG"
            result["error_msg"] = "주변 500m에 정류소가 없어요."            
        else:
            result["result"] = "OK"
            strNearLon = str(cloest_bus_stop['gpslong'])
            strNearLat = str(cloest_bus_stop['gpslati'])
        
            print("최근접 정류소 위도 : " + strNearLat )
            print("최근접 정류소 경도 : " + strNearLon )
        
            # 식별 된 버스 정류장의 도착 정보
            print("정류장 이름 - " + cloest_bus_stop['nodenm']) 
            
            result["near_stop"] = {
                "API" : API,
                "lat" : strNearLat,
                "lon" : strNearLon,
                "name" : cloest_bus_stop['nodenm'],
                "q_param_1" : cloest_bus_stop['citycode'],
                "q_param_2" : cloest_bus_stop['nodeid']
            }            
            
            info = getBusArrivalInfo(cloest_bus_stop['citycode'], cloest_bus_stop['nodeid'])
            result["next_buses"] = info
    
    return result



def getNextBusesOfFavorite(favorite):
    result = {
        "lat" : favorite['lat'],
        "lon" : favorite['lon'],
        "result" : "OK",
        "API" : favorite['API'],
        "near_stop" : {
            "API" : favorite['API'],
            "lat" : favorite['lat'],
            "lon" : favorite['lon'],
            "name" : favorite['name'],
            "q_param_1" : favorite['q_param_1'],
            "q_param_2" : favorite['q_param_2']
            }
        }

    if favorite['API']=='API_SEOUL':
        info = getBusArrivalInfoSeoul(favorite['q_param_1'], favorite['q_param_2'])
        result["next_buses"] = info
            
    else:
        info = getBusArrivalInfo(favorite['q_param_1'], favorite['q_param_2'])
        result["next_buses"] = info
    
    return result