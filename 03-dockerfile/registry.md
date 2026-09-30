# 03-1. Docker Hub에 이미지 push / pull

## 실습 목표

03에서 만든 `myapp` 이미지를 Docker Hub에 올리고, 로컬에서 완전히 지운 뒤 다시 받아서 실행한다.
**"이미지가 없는 다른 컴퓨터에서 이미지 이름 하나로 앱을 실행하는 상황"**을 한 대의 PC로 흉내 내는 것이 목적이다.

## 전체 흐름

```
push  : 내 PC의 이미지 → Docker Hub에 복사본 업로드
rmi   : 내 PC의 이미지만 삭제 (Docker Hub의 복사본은 그대로)
pull  : Docker Hub → 내 PC로 다시 다운로드
```

실무에서는 이 흐름이 여러 컴퓨터에 걸쳐 일어난다.

```
개발자 PC: build → push
                    ↓
               Docker Hub (또는 회사 레지스트리)
                    ↓
서버 A, B, C: pull → run
```

서버에는 코드도 Dockerfile도 필요 없고, 이미지 이름만 있으면 된다.

## 실행한 명령어

```powershell
docker login                                        # 브라우저에서 코드 입력으로 인증
docker tag myapp:1.1 choipumpkin/myapp:1.1          # Docker Hub용 이름표 추가
docker push choipumpkin/myapp:1.1                   # 업로드

docker rm -f myapp                                  # 이미지를 쓰는 컨테이너 먼저 삭제
docker rmi choipumpkin/myapp:1.1 myapp:1.1          # 같은 이미지의 이름표를 전부 제거
docker rmi myapp:1.0                                # 이전 버전도 제거

docker pull choipumpkin/myapp:1.1                   # 다시 다운로드
docker run -d -p 5000:5000 --name myapp choipumpkin/myapp:1.1

docker logout
```

## 이미지 이름 구조

```
레지스트리주소/계정/이미지명:태그
docker.io/choipumpkin/myapp:1.1
```

- 레지스트리 주소를 생략하면 Docker Hub(`docker.io`)
- 계정 자리에는 이메일이 아니라 **Docker Hub 사용자명**
- 이미지 이름에는 대문자 사용 불가
- `docker tag`는 이미지를 복사하지 않고 **이름표만 추가** → 원본과 이미지 ID가 같음
- 실습 PC에 있던 `localhost:5000/challenge/ai2-lab`은 Docker Hub가 아니라 이 PC 5000번 포트의 **비공개 레지스트리**에서 받은 이미지

## 관찰한 것

### push 로그

```
06ad939ed42b: Pushed
3764a9a7d1e8: Pushed
b0dc7f87bef1: Pushed
6b37362b3da7: Mounted from library/nginx
...
```

- `06ad939`, `3764a9a`, `b0dc7f8`은 03 빌드 로그의 `FROM python:3.12-slim` 단계에서 받은 레이어와 **같은 ID**
  → 레이어 ID는 **내용물의 해시(sha256)**라서 내용이 같으면 어디서든 ID가 같음
- `Mounted from library/nginx` → nginx 이미지와 같은 해시의 레이어(Debian 기반 층)가 Docker Hub에 이미 있으므로 **업로드하지 않고 연결만 함**
- python 레이어가 Mounted가 아니라 Pushed였던 이유 → 클라이언트는 자신이 출처를 기록하고 있는 저장소에서만 연결을 시도하는 것으로 보임

### rmi: Untagged와 Deleted

처음에 `docker rmi choipumpkin/myapp:1.1`만 실행했을 때:

```
Untagged: choipumpkin/myapp:1.1
```

- 같은 이미지에 `myapp:1.1` 이름표가 남아 있어서 **이름표만 떼고 데이터는 유지**
- 그래서 바로 pull해도 받을 레이어가 없어 다운로드 줄이 하나도 없었음

이름표를 전부 뗐을 때:

```
Untagged: choipumpkin/myapp:1.1
Untagged: myapp:1.1
Deleted: sha256:0e820b3a...
```

- **마지막 이름표가 떨어질 때만** 실제 삭제(`Deleted`)
- 컨테이너가 사용 중인 이미지는 삭제 불가 → 컨테이너를 먼저 지워야 함

### 완전 삭제 후 pull 로그

```
fe05634e6c2b: Pull complete
c815f020af0f: Pull complete
1e13f19c2da4: Pull complete
de7ab60c6b7c: Pull complete
254b0f73a594: Download complete
```

- push는 9줄, pull은 5줄
- nginx와 공유하는 `6b37362` → `nginx:latest`가 로컬에 남아 있어서 받을 필요 없음
- python 레이어 3개 → `python:3.12-slim` 이미지가 목록에 없는데도 다운로드되지 않음. 이미지를 지워도 레이어 데이터는 저장소에 한동안 남아 있어, 같은 해시를 재사용한 것으로 보임
- **Pull complete**: 다운로드 후 압축 해제까지 완료 (파일 시스템 레이어)
- **Download complete**: 다운로드만 완료. 압축 해제가 필요 없는 메타데이터로 보임

→ push와 pull 모두 **같은 해시의 레이어는 다시 옮기지 않는다**는 원리

## 주의 사항

- Docker Hub 저장소는 기본적으로 **공개(public)** → 이미지 안에 비밀번호, API 키 등을 넣지 않기
- 공용 PC에서는 로그인 전 Docker Desktop에 다른 사람 계정이 로그인되어 있는지 확인
- 실습 후 `docker logout`, Docker Desktop 로그아웃
