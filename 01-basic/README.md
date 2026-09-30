# 01. Docker 기본 명령어

## 실습 목표

이미지로 컨테이너를 실행하고, 상태·로그·내부를 확인한다.

## 실행한 명령어

```powershell
# 환경 확인: Client와 Server가 모두 나와야 정상
docker version

# 첫 컨테이너: 이미지가 없으면 자동 pull → 생성 → 실행 → 종료
docker run hello-world

# 실행 중인 컨테이너만 / 종료된 것까지 전체
docker ps
docker ps -a

# nginx 웹서버를 백그라운드로 실행, 내 PC 8080 → 컨테이너 80 연결
docker run -d -p 8080:80 --name my-nginx nginx

# 컨테이너 출력 확인
docker logs my-nginx

# 중지 / 기존 컨테이너 다시 실행
docker stop my-nginx
docker start my-nginx

# 컨테이너 안으로 들어가기
docker exec -it my-nginx bash
```

컨테이너 내부에서 실행한 명령어:

```bash
cat /etc/os-release                   # 컨테이너 OS 확인
ls /usr/share/nginx/html              # 웹페이지 폴더
cat /usr/share/nginx/html/index.html  # 브라우저에 뜬 페이지의 원본
echo "<h1>Hello from container</h1>" > /usr/share/nginx/html/index.html
exit
```

## 관찰한 것

### hello-world
- `docker ps`에는 안 보이고 `docker ps -a`에만 보임 → 메시지 출력 후 바로 종료되기 때문
- STATUS가 `Exited (0)` → 종료 코드 0은 정상 종료, 0이 아니면 비정상 종료
- 이름을 지정하지 않으면 `youthful_hypatia`처럼 랜덤 이름이 붙음

### nginx 로그
- `OS: Linux ...-microsoft-standard-WSL2`
  → Windows에서 실행했지만 nginx는 **WSL2 리눅스 VM** 위에서 동작. Docker Desktop이 내부에 리눅스 VM을 띄우고 그 안에서 컨테이너를 실행함
- `1#1` → nginx 마스터 프로세스가 컨테이너 안에서 **PID 1**
- 워커 프로세스가 28개 생성 → CPU 코어 수에 맞춰 자동으로 정해짐
- 접속 기록의 IP가 `127.0.0.1`이 아니라 `172.17.0.1`
  → 요청이 Docker 기본 브리지 네트워크(`172.17.0.0/16`)의 게이트웨이를 거쳐 들어오기 때문. 포트 매핑이 실제로는 이 가상 네트워크를 통해 동작함
- `GET / ... 200 896` → `index.html`(896바이트)을 정상 응답
- `GET /favicon.ico ... 404` → 브라우저가 탭 아이콘을 자동 요청했지만 파일이 없어서 404. 문제 아님

### docker ps의 PORTS
- `0.0.0.0:8080->80/tcp` → 이 PC의 **모든 네트워크 인터페이스**에서 포트를 엶. 같은 네트워크의 다른 PC도 접속 가능
- `127.0.0.1:8888->8888/tcp` → **이 PC 자신만** 접속 가능. 외부에 노출할 필요 없는 서비스는 이렇게 묶는 것이 기본 보안 습관

### 컨테이너 내부
- 호스트는 Windows인데 컨테이너 안은 **Debian 13** → 커널은 호스트(WSL2)와 공유하지만 파일 시스템은 이미지 것을 사용
- 프롬프트가 `root@<컨테이너ID>` → 컨테이너 안 기본 사용자는 root, 호스트 이름은 컨테이너 ID
- `/usr/share/nginx/html`에 `index.html`(기본 페이지)과 `50x.html`(서버 에러 페이지)이 있음
- `>`는 덮어쓰기, `>>`는 이어쓰기

## run과 start의 차이

| 명령어 | 동작 |
|---|---|
| `docker run` | 이미지로 **새 컨테이너를 만들어** 실행 |
| `docker start` | **이미 있는 컨테이너**를 다시 실행 |

## 트러블슈팅

### Server 정보 없이 npipe 에러
- **증상**: `docker version`에서 Client만 나오고 아래 에러 발생
  ```
  failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
  ... The system cannot find the file specified.
  ```
- **원인**: Client는 named pipe를 통해 엔진에 명령을 보내는데, Docker 엔진(데몬)이 실행되지 않아 pipe가 존재하지 않음
- **해결**: Docker Desktop 실행 후 **Engine running** 확인, 다시 `docker version`