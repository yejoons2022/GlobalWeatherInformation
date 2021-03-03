import audioop
from ctypes import *
import ktkws # KWS
import MicrophoneStream as MS
import grpc
import gigagenieRPC_pb2
import gigagenieRPC_pb2_grpc
import MicrophoneStream as MS
import user_auth as UA
import os


HOST = 'gate.gigagenie.ai'
PORT = 4080

KWS_KEYWORDS = ['기가지니', '지니야', '친구야', '자기야']

RATE = 16000
CHUNK = 512

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

asound = cdll.LoadLibrary('libasound.so')
asound.snd_lib_error_set_handler(c_error_handler)

def detect_wake_up_word(keyword = '기가지니'):
    if not keyword in KWS_KEYWORDS:
        return False
    response_code = ktkws.init("../data/kwsmodel.pack")
    print('response_code on init = %d' % (response_code))
    response_code = ktkws.start()
    print('response_code on start = %d' % (response_code))
    print('\n호출어를 불러보세요~\n')
    ktkws.set_keyword(KWS_KEYWORDS.index(keyword))

    with MS.MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()

        for content in audio_generator:
            response_code = ktkws.detect(content)

            if response_code == 1:
                MS.play_file("../data/sample_sound.wav")
                print('\n\n호출어가 정상적으로 인식되었습니다.\n\n')
                ktkws.stop()
                return True

def generate_request():
    with MS.MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        for content in audio_generator:
            message = gigagenieRPC_pb2.reqVoice()
            message.audioContent = content
            yield message
            
def get_grpc_stub():
    channel = grpc.secure_channel('{}:{}'.format(HOST, PORT), UA.getCredentials())
    stub = gigagenieRPC_pb2_grpc.GigagenieStub(channel)
    return stub

def get_text_from_voice():
    print("\n\n 음성인식을 시작합니다.\n\n 종료하시려면 Ctrl+\ 키를 누루세요.\n\n\n")
    stub = get_grpc_stub()
    request = generate_request()
    resultText = ''
    for response in stub.getVoice2Text(request):
        if response.resultCd == 200: # partial
            print('상태 코드=%d | 인식 결과= %s'% (response.resultCd, response.recognizedText))
            resultText = response.recognizedText
        elif response.resultCd == 201: # final
            print('상태 코드=%d | 인식 결과= %s'% (response.resultCd, response.recognizedText))
            resultText = response.recognizedText
            break
        else:
            print('상태 코드=%d | 인식 결과= %s'% (response.resultCd, response.recognizedText))
            break
    print("\n\n 최종 인식 결과: %s \n\n" % (resultText))
    return resultText

def get_voice_from_text(text, output_file_name = 'tts.wav'):
    stub = get_grpc_stub()
    message = gigagenieRPC_pb2.reqText()

    message.lang = 0 # 0: 한국어, 1: 영어
    message.text = text

    with open(output_file_name, 'wb') as output:
        for response in stub.getText2VoiceStream(message):
            result_code = response.resOptions.resultCd
            print("\n\n 음성합성 응답 상태코드:", result_code)

            if result_code == 200 or result_code == 0:
                output.write(response.audioContent)
            else:
                return False
    return True

def speech(text):
    result_code = get_voice_from_text(text)
    if result_code == True:
        MS.play_file('tts.wav')
        print('음성이 출력되었습니다.')
    else:
        print('에러가 발생하였습니다.')
        
def query_by_text(text):
    stub = get_grpc_stub()
    message = gigagenieRPC_pb2.reqQueryText()
    message.queryText = text
    message.userSession = "1234" # 단말기의 관리를 위해 넣어놓는 변수들
    message.deviceId = "yourdevice" # 현재는 쓰이지 않으나 추후 사용 예정
    
    response = stub.queryByText(message)

    print("\n\nresultCd: %d" % (response.resultCd))

    if response.resultCd == 200:
        print("\n\n\n 질의한 내용: %s" % (response.uword))
        for action in response.action:
            query_response = action.mesg

        query_response = query_response.replace('<![CDATA[', '').replace(']]>', '')
        return query_response

    else:
        return None

    
if __name__ == '__main__':
    if detect_wake_up_word():
        recognized_text = get_text_from_voice()
        result = query_by_text(recognized_text)
        print(result)
        speech(result)
