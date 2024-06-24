from flask import Flask, render_template, request, make_response
import api_functions

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('./index.html', ncp_client_id = api_functions.NVR_KEY_ID)


@app.route('/buses', methods=['POST'])
def bus():
    data = request.json
        
    strLat = data['lat']
    strLon = data['lon']
    result = api_functions.getNextBuses(strLat, strLon)
    return result


@app.route('/bus', methods=['POST'])
def busshow():

    strLat = request.form.get('lat')
    strLon = request.form.get('lon')


    result = api_functions.getNextBuses(strLat, strLon)
    
    if result['result']=='NG':
        return render_template('./error.html', 
                           lat = result['lat'],
                           lon = result['lon'],
                           error_msg = result['error_msg']
    )
        
    return render_template('./bus.html', 
                           lat = result['lat'],
                           lon = result['lon'],
                           near_stop = result['near_stop'],
                           next_buses = list(result['next_buses'].items()),
                           ncp_client_id = api_functions.NVR_KEY_ID
    )

    
@app.route('/favorite', methods=['GET','POST'])
def favorite():
    new_fav = None
    
    if request.method == 'POST':
        print("New Favorite")
        new_fav = {
                "API" : request.form.get('API'),
                "lat" : request.form.get('lat'),
                "lon" : request.form.get('lon'),
                "name" : request.form.get('name'),
                "q_param_1" : request.form.get('q_param_1'),
                "q_param_2" : request.form.get('q_param_2')
        }       
    elif request.method == 'GET':
        print("Load Favorite")
        # 일단 쿠기가 있다면 그것으로 초기화
        favorite_string = request.cookies.get('favorite')
        if favorite_string:
            favorite_dict = api_functions.cookieString2DictObj(favorite_string)
            if favorite_dict['name'] != None:
                new_fav = favorite_dict
    
    print(new_fav)
            
    # 즐겨 찾기가 있다면...
    if new_fav:
        result = api_functions.getNextBusesOfFavorite(new_fav)
        
        resp = make_response(render_template('./bus.html', 
                            lat = result['lat'],
                            lon = result['lon'],
                            near_stop = result['near_stop'],
                            next_buses = list(result['next_buses'].items()),
                            ncp_client_id = api_functions.NVR_KEY_ID
        ))
        
        #쿠기 저장용 문자열로 변환
        favorite_string = api_functions.dictObj2CookieString(new_fav)
        resp.set_cookie('favorite', favorite_string)        
        return resp

    return render_template('./error.html', 
                    error_msg = '즐겨찾기 정보가 올바르지 않아요.')


if __name__ == '__main__':
    app.run(debug=True)