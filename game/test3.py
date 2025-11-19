import sys,os,subprocess,pickle,random


try:
    import pygame
except ImportError:
    print("pygame이 설치되어 있지 않습니다. 자동으로 설치를 시도합니다...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        import pygame
    except Exception as e:
        print("pygame 설치 실패:", e)
        sys.exit(1)
#pygame 설치



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
           ,"...............","(폰을 하고 있는 학생을 클릭해 검거하자!)","다 잡았다"]
endscripts = ["나는 학생들의 몰폰을 잡으려고 했지만, 아무런 수확이 없었다.","그 이후로 나는 학생들에게 만만하게 여겨져 학생들이 마구잡이로 룰을 어기게 되었다.","엔딩1:몰폰의 시대"
              ,"1","2","엔딩2끝"]
curscript = ""#출력될 대화
text_index = 0#한 대화의 문자열 번호
delay = 75#문자출력간 시간
last_time = 0#전 타자시간,전시간
istalking=True#대화중인지
storynum = 0 #스토리넘버

students = [[3,3,1,3,1,3]]#0:비어있음 1: 자고있음1, 2:자고있음2, 3:당당히 폰함, 4:갑자기 숨김,5:이불속에서 함,
#7:갑자기 숨김변화후이미지,6:중간에 도망침,8:도망침이미지,9:도망침자리이미지
# 11:반항아(힘으로 이겨야함(광클),지면 도망) / 그후로는 뇌절생각중 9:음악러(리듬게임) 10:전교1등(퀴즈맞추기) 11:포켓몬 마스터...
studentimg = ["student2.png","student2.png","student3.png","student1.png","student1.png","student4.png",
              "student5.png","student2.png","student5-1.png","student5-1.png"]#학생이미지

doors = [0,0,0,0,0,0,0,0,0,0]#문상태
curdoor=0
running = True
wholestream=0#0>튜토리얼 1>메인화면 2>설명 3>로비 4>호실안 5>결과 출력,엔딩
explainpage=0#로비페이지
studentsexplain = ["그저 비어있음","자고 있는 착한 학생(잡으면 -2)","이불속에서 자고 있는 착한 학생(잡으면 -2)","사감쌤이 왔는데도 당당히 폰하는 학생(클릭해 잡기)",
                   "숨기는 학생(시간이 지나면 자는 학생처럼 겉모습이 바뀜,기억했다가 잡기)","이불속에서 하는 학생(그냥잡기)"]
sounds = ["death.wav","brah.wav","pew.mp3","byam.mp3","afew.mp3"]
score=0

#함수존
def set_studentimg(num,x,y):
    img = pygame.image.load(studentimg[num])
    if(num!=0 and num!=9):
        screen.blit(img, (x, y))

def get_score(whereclick):
    global score
    if students[curdoor][whereclick]>2:
        if students[curdoor][whereclick]!=9:
            score+=1
            students[curdoor][whereclick]=0
            pygame.mixer.music.load(sounds[random.randint(0, 3)])
            pygame.mixer.music.play()
    elif students[curdoor][whereclick]<=2 and students[curdoor][whereclick]>0:
        score-=2
        students[curdoor][whereclick]=0
        pygame.mixer.music.load(sounds[random.randint(0, 3)])
        pygame.mixer.music.play()

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

while running:#무한함수 > 실행중
    font = pygame.font.Font("C:/Windows/Fonts/malgun.ttf", 30)#기본폰트
    if data.get('튜토리얼')==1 and wholestream==0:
        wholestream=1







    #이벤트 처리
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False#게임종료

        if event.type == pygame.MOUSEBUTTONDOWN:# 마우스 클릭
            if(wholestream==0):
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
                            pygame.mixer.music.load(sounds[4])
                            pygame.mixer.music.play()
                        if(textnum==6):
                            storynum+=1
                        if(textnum==7):
                            storynum+=1
            elif(wholestream==1):
                x, y = pygame.mouse.get_pos()
                if x>300 and x<900 and y>525 and y<675:#game시작
                    wholestream=3
                    students = [[random.randint(0, 6) for _ in range(6)] for _ in range(10)]
                    print(students)
                if x>1050 and x<1200 and y<200:
                    wholestream=2
            elif(wholestream==2):
                x, y = pygame.mouse.get_pos()
                if x>1050 and x<1200 and y<200:
                    wholestream=1
                if x>1050 and x<1200 and explainpage<5:
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
                        if students[curdoor][i]==9:
                            a = 20+400*int(i/2)-( pygame.time.get_ticks() - last_time - 700)/2
                            if x> a and x<a+200 and y>500:
                                score+=1
                                students[curdoor][i]=0
                                pygame.mixer.music.load(sounds[random.randint(0, 3)])
                                pygame.mixer.music.play()
                if x<350 and y<300:#1
                    get_score(0)
                elif x<350 and y>300 and y<500:#2
                    get_score(1)
                elif x>350 and x<700 and y<300:#3
                    get_score(2)
                elif x>350 and x<700 and y>300 and y<500:#4
                    get_score(3)
                elif x>700 and x<1050 and y<300:#5
                    get_score(4)
                elif x>700 and x<1050 and y>300 and y<500:#6
                    get_score(5)
                elif x>1050 and x<1200 and y<200:
                    wholestream=3
                    '''for i in range(6):#다검거했는지 확인
                        if students[curdoor][i]>2:
                            break
                        if i==5:'''
            elif(wholestream==5):
                if(text_index < len(endscripts[textnum])):#대화출력중일시
                    text_index = len(endscripts[textnum])#대화=full대화
                    curscript = endscripts[textnum]
                elif textnum ==2 or textnum==5:#더이상의 대화 없으면,대화끊기
                    curscript=""
                    istalking = False
                else:#다음대화 넘어가야 할때
                    textnum+=1
                    curscript=""
                    text_index=0



    #화면 그리기



    if(wholestream==0):
        if(storynum==0):
            img = pygame.image.load("background1.png")  # 이미지 불러오기
            screen.blit(img, (0, 0))
        elif(storynum==1):
            img = pygame.image.load("afew.png")  # 이미지 불러오기
            screen.blit(img, (0, 0))
        elif(storynum==2):
            img = pygame.image.load("background2.png")  # 이미지 불러오기
            screen.blit(img, (0, 0))
        elif(storynum==3):
            screen.fill((255,255,255))
            img = pygame.image.load("bed.png")  # 이미지 불러오기
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
            img = pygame.image.load("pannel.png")  # 이미지 불러오기
            screen.blit(img, (100, 575))
        #pygame.draw.rect(screen, (0,0,255), (100, 575, 1000, 100))  # 사각형

        # 일정 시간이 지나면 다음 글자 추가
        if istalking:
            now = pygame.time.get_ticks()

            if text_index < len(scripts[textnum]) and now - last_time >= delay:
                curscript += scripts[textnum][text_index]
                text_index += 1
                last_time = now


            text = font.render(curscript, True, (0, 0, 0))  # 글자 렌더링
            screen.blit(text, (140, 600))  # 출력
    elif wholestream==1:
        img = pygame.image.load("background3.png")  # 이미지 불러오기
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
        img = pygame.image.load("background4.png")  # 이미지 불러오기
        screen.blit(img, (0, 0))
        img = pygame.image.load("openeddoor.png")
        for i in range(5):
            if doors[i]==1:
                screen.blit(img, (82+219*i, 42))
        for i in range(5,10):
            if doors[i]==1:
                screen.blit(img, (82+219*(i-5), 383))
        for i in range(10):
            if doors[i]==0:
                break
            if i==9:
                if score<0:
                    textnum=0
                elif score < 10:
                    textnum=3
                wholestream=5
                istalking=True
        text = font.render(str(score), True, (0, 0, 0))  # 글자 렌더링
        screen.blit(text, (1100, 0))  # 출력
    elif wholestream==4:
        screen.fill((255,255,255))
        img = pygame.image.load("bed.png")  # 이미지 불러오기
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
        img = pygame.image.load("out.png")  # 이미지 불러오기
        screen.blit(img, (1000, 50))
        if pygame.time.get_ticks() - last_time >= 500:
            for i in range(6):
                if students[curdoor][i]==4:
                    students[curdoor][i]=7
        if pygame.time.get_ticks() - last_time >= 700:
            for i in range(6):
                if students[curdoor][i]==6 or students[curdoor][i]==9:
                    students[curdoor][i]=9
                    set_studentimg(8,20+400*int(i/2)-( pygame.time.get_ticks() - last_time - 700)/2,500)
    elif wholestream==5:
        screen.fill((255,255,255))
        text = font.render(str(score), True, (0, 0, 0))  # 글자 렌더링
        screen.blit(text, (1100, 0))  # 출력
        if istalking:
            now = pygame.time.get_ticks()

            if text_index < len(endscripts[textnum]) and now - last_time >= delay:
                curscript += endscripts[textnum][text_index]
                text_index += 1
                last_time = now

            text = font.render(curscript, True, (0, 0, 0))  # 글자 렌더링
            screen.blit(text, (140, 600))  # 출력
    pygame.display.flip()  # 화면 업데이트

    #FPS 제한
    clock.tick(60)

pygame.quit()
sys.exit()