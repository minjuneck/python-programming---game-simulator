import sys,os,subprocess,pickle,random
from io import BytesIO

try:
    import pygame
except ImportError:
    print("pygame이 설치되어 있지 않습니다. 자동으로 설치를 시도합니다...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
    import pygame
#pygame 설치
try:
    import requests
    print("requests 이미 설치됨")

except ImportError:
    print("requests 없음 → 설치 시도 중...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests
#request 설치



pygame.init()  # pygame 초기화
pygame.mixer.init()
screen = pygame.display.set_mode((1200, 700))  # 창 크기 설정
pygame.display.set_caption("기숙사에서 몰폰 잡기 시뮬레이션")  # 창 제목 설정
clock = pygame.time.Clock()  # FPS(초당 프레임 수) 관리용



#저장기능들
data = {"튜토리얼":0}
def savedata():
    with open('data.pkl', "wb") as f:
        pickle.dump(data, f)
def loaddata():
    global data
    if os.path.exists('data.pkl'):
        try:
            with open('data.pkl', 'rb') as f:
                data = pickle.load(f)
            print(f"✅ 기존 데이터 '{'data.pkl'}'를 성공적으로 불러왔습니다.")
        except Exception as e:
            # 파일은 있지만, 내용이 손상되었거나 형식이 잘못된 경우 발생할 수 있는 에러 처리
            print(f"❌ 파일은 존재하지만 불러오는 중 에러 발생 ({e}). 빈 데이터로 초기화합니다.")
    else:
        print(f"⚠️ 저장 파일 '{'data.pkl'}'이 존재하지 않습니다. 빈 데이터로 초기화합니다.")
loaddata()

#변수관리
textnum =0 #대화번호
scripts = ["학생1: 404호 현원 다섯명 **이 안왔습니다","학생2: 405호 6명 이상무","나:어 그래 밤에 핸드폰 하지 말고, 점호 끝!"
           ,"학생들:와와아!","","(분명 몰래 폰하는 학생들이 있을 것이다,한번 검거해 보자)","(문을 클릭해 호실 들어가기)"
           ,"...............","(폰을 하고 있는 학생을 클릭해 검거하자!)","튜토리얼 끝"]
endscripts = ["나는 학생들의 몰폰을 잡으려고 했지만, 아무런 수확이 없었다.","그 이후로 나는 학생들에게 만만하게 여겨져 학생들이 마구잡이로 룰을 어기게 되었다.","엔딩1:몰폰의 시대(배드엔딩)"
              ,"어느정도 잡긴 했지만 많이 놓쳤다","뭐 애들이 어느정도는 경각심을 갖겠지","엔딩2 평범한 하루(노멀엔딩)",
              "꽤 많이 잡았네","이젠 앞으로 몰폰 할 생각은 안하겠지","엔딩3 몰폰의 몰락(노멀엔딩)",
              "이렇게 몰폰하는 학생이 많았어?","이제 더이상은 못한다","엔딩4 몰폰의 끝(노멀엔딩)",
              "몰폰(히든엔딩)"]
curscript = ""#출력될 대화
text_index = 0#한 대화의 문자열 번호
delay = 75#문자출력간 시간
last_time = 0#전 타자시간,전시간
tugging=False#힘쌘학생전용
tugpoint=0
curtugstudent=-1
musicing=0
musictile=[]
istalking=True#대화중인지
storynum = 0 #스토리넘버

students = [[3,3,1,3,1,3]]#0:비어있음 1: 자고있음1, 2:자고있음2, 3:당당히 폰함, 4:갑자기 숨김,5:이불속에서 함,
#10:갑자기 숨김변화후이미지,6:중간에 도망침,11:도망침이미지,12:도망침자리이미지
# 7:힘쌘학생(힘으로 이겨야함(광클),지면 도망) / 그후로는 뇌절생각중 8:음악러(리듬게임) 10:전교1등(퀴즈맞추기) 11:포켓몬 마스터...
studentimg = ["student2.png","student2.png","student3.png","student1.png","student1.png","student4.png",
              "student5.png","student6.png","student1.png","student1.png","student2.png","student5-1.png","student5-1.png"]#학생이미지

doors = [0,0,0,0,0,0,0,0,0,0]#문상태
curdoor=0
running = True
wholestream=0#0>튜토리얼 1>메인화면 2>설명 3>로비 4>호실안 5>결과 출력,엔딩 6>히든 학생
explainpage=0#로비페이지
studentsexplain = ["그저 비어있음","자고 있는 학생(잡으면 -2)","이불속에서 자고 있는 학생(잡으면 -2)","사감쌤이 왔는데도 당당히 폰하는 학생(클릭해 잡기)",
                   "숨기는 학생(시간이 지나면 자는 학생처럼 겉모습이 바뀜,기억했다가 잡기)","이불속에서 하는 학생(그냥잡기)","도망치는 학생(시간이 지나면 화면 왼쪽으로 도망감,도망가는 것을 클릭해 잡기)","힘쌘 학생(누르고 광클해서 잡기 게이지가 없어지면 놓침)"]

sounds = ["death.wav","brah.wav","pew.mp3","byam.mp3","afew.mp3"]
score=0
#####################################################
CACHE_DIR = "cache"
BASE_URL = "https://raw.githubusercontent.com/minjuneck/python-programming---game-simulator/main/game/"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
def download_and_cache(filename):
    local_path = os.path.join(CACHE_DIR, filename)
    url = BASE_URL + filename

    # 이미 캐시에 있으면 다운로드 생략
    if os.path.exists(local_path):
        return local_path

    print(f"[DOWNLOAD] {filename} 다운로드 중...")

    data = requests.get(url).content

    with open(local_path, "wb") as f:
        f.write(data)

    return local_path
PRELOAD_IMAGES = [
    "afew.png",
    "background1.png",
    "background2.png",
    "background3.png",
    "background4.png",
    "bed.png",
    "openeddoor.png",
    "out.png",
    "pannel.png",
    "student1.png",
    "student2.png",
    "student3.png",
    "student4.png",
    "student5.png",
    "student5-1.png",
    "student6.png",
]
PRELOAD_SOUNDS = [
    "afew.mp3",
    "brah.wav",
    "byam.mp3",
    "death.wav",
    "pew.mp3",
    "pop.mp3",
]

def preload_all_images():
    print("=== 이미지 Preload 시작 ===")
    for img in PRELOAD_IMAGES:
        download_and_cache(img)
    print("=== Preload 완료 ===")

def preload_all_sounds():
    print("=== 사운드 Preload 시작 ===")
    for snd in PRELOAD_SOUNDS:
        download_and_cache(snd)
    print("=== 사운드 Preload 완료 ===")

def setimage(filename):
    path = download_and_cache(filename)  # 캐시된 파일 경로 가져오기
    return pygame.image.load(path)

def loadsound(filename):
    path = download_and_cache(filename)
    return pygame.mixer.Sound(path)
###################################################
#함수존

def set_studentimg(num,x,y):
    img = setimage(studentimg[num])
    if(num!=0 and num!=12):#111111111111111111111111111111111
        screen.blit(img, (x, y))

def get_score(whereclick):
    global score
    global tugging
    global curtugstudent
    global tugpoint
    global wholestream
    global musicing
    global musictile
    if students[curdoor][whereclick]>2:
        if students[curdoor][whereclick]!=12 and students[curdoor][whereclick]!=7 and students[curdoor][whereclick]!=8 and students[curdoor][whereclick]!=9:#111111111111111111111
            score+=1
            students[curdoor][whereclick]=0
            loadsound(sounds[random.randint(0, 3)]).play()
        elif(students[curdoor][whereclick]==7):
            tugging=True
            tugpoint =10
            curtugstudent=whereclick
        elif(students[curdoor][whereclick]==8):
            musicing=1
            musictile = [random.randint(0,1) for _ in range(6)]
            print(musictile)
    elif students[curdoor][whereclick]<=2 and students[curdoor][whereclick]>0:
        score-=2
        students[curdoor][whereclick]=0
        loadsound(sounds[random.randint(0, 3)]).play()

def opendoor(num):
        global doors
        global wholestream
        global curdoor
        global last_time
        if(doors[num]==0):
            doors[num]=1
            wholestream=4
            curdoor=num
            last_time =pygame.time.get_ticks()

preload_all_images()
preload_all_sounds()
while running:#무한함수 > 실행중
    font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 30)#기본폰트
    if data.get('튜토리얼')==1 and wholestream==0:
        wholestream=1







    #이벤트 처리
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False#게임종료

        if event.type == pygame.MOUSEBUTTONDOWN:# 마우스 클릭
            if(tugging):
                tugpoint+=7
            elif(wholestream==0):
                if(text_index < len(scripts[textnum])):#대화출력중일시
                    text_index = len(scripts[textnum])#대화=full대화
                    curscript = scripts[textnum]
                else:
                    if istalking==False:#대화 아니면
                        x, y = pygame.mouse.get_pos()
                        if x<350 and y<300:#1
                            get_score(0)
                        elif x<350 and y>300:#2
                            get_score(1)
                        elif x>350 and x<700 and y<300:#3
                            get_score(2)
                        elif x>350 and x<700 and y>300:#4
                            get_score(3)
                        elif x>700 and x<1050 and y<300:#5
                            get_score(4)
                        elif x>700 and x<1050 and y>300:#6
                            get_score(5)
                        for i in range(6):#다검거했는지 확인
                            if students[0][i]>2:
                                break
                            if i==5:
                                textnum+=1
                                istalking=True
                                text_index=0

                    elif textnum == 8 or textnum==9:#더이상의 대화 없으면,대화끊기
                        curscript=""
                        istalking = False
                        if textnum==9:
                            data.update(튜토리얼=1)
                            savedata()
                    else:#다음대화 넘어가야 할때
                        textnum+=1
                        curscript=""
                        text_index=0
                        if(textnum==4):
                            storynum+=1
                            loadsound(sounds[4]).play()
                        if(textnum==6):
                            storynum+=1
                        if(textnum==7):
                            storynum+=1
            elif(wholestream==1):
                x, y = pygame.mouse.get_pos()
                if x>300 and x<900 and y>525 and y<675:#game시작
                    wholestream=3
                    students = [[random.randint(0, 2) for _ in range(6)] for _ in range(10)]
                    for i in range(40):
                        while 1:
                            j,k=random.randint(0, 9),random.randint(0, 5)
                            if students[j][k] <= 2:
                                students[j][k] = random.randint(3, 8)
                                break

                    print(students)
                if x>1050 and x<1200 and y<200:
                    wholestream=2
            elif(wholestream==2):
                x, y = pygame.mouse.get_pos()
                if x>1050 and x<1200 and y<200:
                    wholestream=1
                if x>1050 and x<1200 and explainpage<7:
                    explainpage+=1
                if x>0 and x<150 and explainpage>0:
                    explainpage-=1
            elif(wholestream==3):
                x, y = pygame.mouse.get_pos()
                if x>82 and x<259 and y>44 and y<319:
                    opendoor(0)
                elif x>301 and x<478  and y>44 and y<319:
                    opendoor(1)
                elif x>520 and x<697  and y>44 and y<319:
                    opendoor(2)
                elif x>739 and x< 916 and y>44 and y<319:
                    opendoor(3)
                elif x>958 and x<1135 and y>44 and y<319:
                    opendoor(4)
                elif x>82  and x<259  and y>383 and y<658:
                    opendoor(5)
                elif x>301 and x<478  and y>383 and y<658:
                    opendoor(6)
                elif x>520 and x<697  and y>383 and y<658:
                    opendoor(7)
                elif x>739 and x< 916 and y>383 and y<658:
                    opendoor(8)
                elif x>958 and x<1135 and y>383 and y<658:
                    opendoor(9)
            elif(wholestream==4):
                x, y = pygame.mouse.get_pos()
                if pygame.time.get_ticks() - last_time >= 700:
                    for i in range(6):
                        if students[curdoor][i]==12:##########
                            a = 20+400*int(i/2)-( pygame.time.get_ticks() - last_time - 700)/2
                            if x> a and x<a+200 and y>550:
                                score+=1
                                students[curdoor][i]=0
                                loadsound(sounds[random.randint(0, 3)]).play()
                if x<350 and y<300:#1
                    get_score(0)
                elif x<350 and y>300 and y<550:#2
                    get_score(1)
                elif x>350 and x<700 and y<300:#3
                    get_score(2)
                elif x>350 and x<700 and y>300 and y<550:#4
                    get_score(3)
                elif x>700 and x<1050 and y<300:#5
                    get_score(4)
                elif x>700 and x<1050 and y>300 and y<550:#6
                    get_score(5)
                elif x>1050 and x<1200 and y<200:
                    wholestream=3

            elif(wholestream==5):
                if(text_index < len(endscripts[textnum])):#대화출력중일시
                    text_index = len(endscripts[textnum])#대화=full대화
                    curscript = endscripts[textnum]
                elif textnum ==2 or textnum==5 or textnum==8 or textnum==11:#더이상의 대화 없으면,대화끊기
                    curscript=""
                    istalking = False
                else:#다음대화 넘어가야 할때
                    textnum+=1
                    curscript=""
                    text_index=0




    #화면 그리기



    if(wholestream==0):
        if(storynum==0):
            img = setimage("background1.png")  # 이미지 불러오기
            screen.blit(img, (0, 0))
        elif(storynum==1):
            img = setimage("afew.png")  # 이미지 불러오기
            screen.blit(img, (0, 0))
        elif(storynum==2):
            img = setimage("background2.png")  # 이미지 불러오기
            screen.blit(img, (0, 0))
        elif(storynum==3):
            screen.fill((255,255,255))
            img = setimage("bed.png")  # 이미지 불러오기
            screen.blit(img, (10, 100))
            screen.blit(img, (410, 100))
            screen.blit(img, (810, 100))
            set_studentimg(students[0][0],20,100)
            set_studentimg(students[0][1],20,350)
            set_studentimg(students[0][2],420,100)
            set_studentimg(students[0][3],420,350)
            set_studentimg(students[0][4],820,100)
            set_studentimg(students[0][5],820,350)
            text = font.render(str(score), True, (0, 0, 0))  # 글자 렌더링
            screen.blit(text, (1100, 0))  # 출력
        if istalking:
            img = setimage("pannel.png")  # 이미지 불러오기
            screen.blit(img, (100, 575))
        #pygame.draw.rect(screen, (0,0,255), (100, 575, 1000, 100))  # 사각형

        # 일정 시간이 지나면 다음 글자 추가
        if istalking:
            now = pygame.time.get_ticks()

            if text_index < len(scripts[textnum]) and now - last_time >= delay:
                curscript += scripts[textnum][text_index]
                text_index += 1
                last_time = now
                loadsound("pop.mp3").play()

            text = font.render(curscript, True, (0, 0, 0))  # 글자 렌더링
            screen.blit(text, (140, 600))  # 출력
    elif wholestream==1:
        img = setimage("background3.png")  # 이미지 불러오기
        screen.blit(img, (0, 0))
    elif wholestream==2:
        screen.fill((255,255,255))
        font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 150)
        text = font.render(">", True, (0, 0, 0))  # 글자 렌더링
        screen.blit(text, (1100, 200))  # 출력
        text = font.render("<", True, (0, 0, 0))  # 글자 렌더링
        screen.blit(text, (0, 200))  # 출력
        set_studentimg(explainpage,500,100)
        font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 30)
        text = font.render(studentsexplain[explainpage], True, (0, 0, 0))  # 글자 렌더링
        screen.blit(text, (100, 400))  # 출력
        text = font.render("메인화면으로", True, (0, 0, 0))  # 글자 렌더링
        screen.blit(text, (1000, 50))  # 출력
    elif wholestream==3:
        img = setimage("background4.png")  # 이미지 불러오기
        screen.blit(img, (0, 0))
        img = setimage("openeddoor.png")
        for i in range(5):
            if doors[i]==1:
                screen.blit(img, (80+220*i, 40))
        for i in range(5,10):
            if doors[i]==1:
                screen.blit(img, (80+220*(i-5), 380))
        for i in range(10):
            if doors[i]==0:
                break
            if i==9:
                if score<=5:
                    textnum=0
                elif score <= 20:
                    textnum=3
                elif score <=40:
                    textnum=6
                else:
                    textnum=9
                wholestream=5
                istalking=True
        text = font.render(str(score), True, (0, 0, 0))  # 글자 렌더링
        screen.blit(text, (1100, 0))  # 출력
    elif wholestream==4:
        screen.fill((255,255,255))
        img = setimage("bed.png")  # 이미지 불러오기
        screen.blit(img, (10, 100))
        screen.blit(img, (410, 100))
        screen.blit(img, (810, 100))
        set_studentimg(students[curdoor][0],20,100)
        set_studentimg(students[curdoor][1],20,350)
        set_studentimg(students[curdoor][2],420,100)
        set_studentimg(students[curdoor][3],420,350)
        set_studentimg(students[curdoor][4],820,100)
        set_studentimg(students[curdoor][5],820,350)
        text = font.render(str(score), True, (0, 0, 0))  # 글자 렌더링
        screen.blit(text, (1100, 0))  # 출력
        img = setimage("out.png")  # 이미지 불러오기
        screen.blit(img, (1000, 50))
        if pygame.time.get_ticks() - last_time >= 500:
            for i in range(6):
                if students[curdoor][i]==4:
                    students[curdoor][i]=10########
        if pygame.time.get_ticks() - last_time >= 700:
            for i in range(6):
                if students[curdoor][i]==6 or students[curdoor][i]==12:##########
                    students[curdoor][i]=12
                    set_studentimg(11,20+400*int(i/2)-( pygame.time.get_ticks() - last_time - 700)/2,550)
    elif wholestream==5:
        img = setimage("background1.png")  # 이미지 불러오기
        screen.blit(img, (0, 0))
        text = font.render(str(score), True, (0, 0, 0))  # 글자 렌더링
        screen.blit(text, (1100, 0))  # 출력
        if istalking:
            now = pygame.time.get_ticks()

            if text_index < len(endscripts[textnum]) and now - last_time >= delay:
                curscript += endscripts[textnum][text_index]
                text_index += 1
                last_time = now
                loadsound("pop.mp3").play()

            text = font.render(curscript, True, (0, 0, 0))  # 글자 렌더링
            screen.blit(text, (140, 600))  # 출력
    if(tugging):
        pygame.draw.rect(screen, (0,0,0), (100, 50,1000,150))
        pygame.draw.rect(screen, (0,0,255), (100, 50,10*tugpoint,150))
        if(pygame.time.get_ticks() % 3==0):
            tugpoint-=1
        if(tugpoint>=100):
            tugging=0
            tugging=False
            score+=1
            students[curdoor][curtugstudent]=0
            curtugstudent=-1
            loadsound(sounds[random.randint(0, 3)]).play()
        elif(tugpoint<0):
            tugging=0
            students[curdoor][curtugstudent]=0
    if(musicing):

    pygame.display.flip()  # 화면 업데이트

    #FPS 제한
    clock.tick(60)

pygame.quit()
sys.exit()