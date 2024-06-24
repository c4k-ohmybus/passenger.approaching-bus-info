<br/>
<br/>

<p align="center">
<img src="https://codefor.kr/rails/active_storage/representations/redirect/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBMWdzQWc9PSIsImV4cCI6bnVsbCwicHVyIjoiYmxvYl9pZCJ9fQ==--0b83a5866491632c84a1a9eaa74b68bb793cd5da/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaDdCem9MWm05eWJXRjBTU0lJY0c1bkJqb0dSVlE2RkhKbGMybDZaVjkwYjE5c2FXMXBkRnNIYVFLUUFXa0NrQUU9IiwiZXhwIjpudWxsLCJwdXIiOiJ2YXJpYXRpb24ifX0=--537c8e94e5de06fa6d39e4d7e8743b927489cf51/19755d27-1790-460b-a901-77bb539d71c8.png" width="50%" alt="Code for Korea"/>
</p>

<br/>
<br/>

# 내 버스 언제와?

낯선 곳에서 하염없이 버스를 기다리는 여행자, 외지인 혹은 현지인에게 버스 도착 정보를 알려 하염없는 기다림의 고통을 덜어주고자 하는 서비스입니다.

## 버스 도착 정보 출처

### 국토부 버스정보 API(TAGO)에서 지원하는 지역
- 국토교통부_(TAGO)_버스정류소정보
- 국토교통부_(TAGO)_버스도착정보

### 국토부 버스정보 API(TAGO)에서 지원하지 않는 지역
- 해당 지자체에서 별도의 버스 정보 API를 제공 할 경우, 이를 사용
- 확인 된 지역 : 서울(서울특별시_정류소정보조회 서비스)

### 지역 식별 방법
- GPS 좌표로 Reverse Geocoding하여 주소를 얻고, 주소의 시군구 정보로 지자체 별도 제공 API 지역인지 판별하여 분기 (Naver Map API 사용)


## 환경변수

### 국토부 TAGO API 사용 Key
- DATA_GO_DEC : decoding key
- DATA_GO_ENC : encoding key

### Naver Map API
- NVR_KEY_ID : Naver Map API Key ID
- NVR_KEY_SECRET : Naver Map API Secret

