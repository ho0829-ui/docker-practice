# 04. Docker Compose로 Flask + Redis 구성

## 실습 목표

웹 앱과 Redis, 두 컨테이너를 Compose로 함께 띄우고, 컨테이너 간 통신과 데이터 유지 방식을 확인한다.

## Compose가 필요한 이유

`docker run`으로 여러 컨테이너를 운영하면:

1. 포트, 볼륨, 이름 옵션을 컨테이너마다 매번 입력해야 함
2. 실행 순서(DB 먼저, 앱 나중)를 사람이 기억해야 함
3. 컨테이너끼리 통신하려면 네트워크를 직접 만들고 연결해야 함

Compose는 이 설정을 **YAML 파일 하나에 정의하고 명령어 한 줄로 실행**한다.

## 파일 구성

```
04-compose/
├─ compose.yaml
├─ Dockerfile        (03과 동일)
├─ .dockerignore
├─ app.py            (접속할 때마다 Redis의 방문 횟수를 1 증가)
└─ requirements.txt  (flask, redis)
```

## compose.yaml 해설

```yaml
services:
  web:
    build: .                 # 현재 폴더의 Dockerfile로 빌드
    ports:
      - "5000:5000"          # -p 5000:5000
    depends_on:
      - redis                # redis를 먼저 띄운 뒤 web 실행

  redis:
    image: redis:7-alpine    # 이미 있는 이미지 사용
    command: redis-server --appendonly yes   # 이미지 기본 CMD 대체, 데이터를 파일에 계속 기록
    volumes:
      - redis-data:/data     # 이름 있는 볼륨 연결

volumes:
  redis-data:                # 볼륨 선언 (Docker가 관리하는 저장 공간)
```

## 실행한 명령어

```powershell
docker rm -f myapp                 # 5000번 포트를 쓰던 컨테이너 정리
docker compose up -d --build       # 빌드 후 전체 실행
docker compose ps                  # 상태 확인

# web 컨테이너 안에서 'redis'라는 이름이 어떤 IP로 바뀌는지 확인
docker compose exec web python -c "import socket; print(socket.gethostbyname('redis'))"
docker network ls

docker compose down                # 컨테이너 + 네트워크 삭제
docker compose up -d
docker compose down -v             # 볼륨까지 삭제
docker compose up -d
```

## 관찰한 것

### 서비스 이름으로 통신

```
redis → 172.19.0.2
```

- `app.py`에서 IP 대신 `host="redis"`로 접속 가능한 이유
  → Compose가 만든 **`04-compose_default` 네트워크의 내장 DNS**가 서비스 이름을 컨테이너 IP로 알려줌
- 01의 nginx는 기본 `bridge` 네트워크(`172.17.x.x`), 지금은 Compose 전용 네트워크(`172.19.x.x`)
- 기본 `bridge` 네트워크에는 이름 해석 기능이 없어서 Compose는 프로젝트마다 네트워크를 따로 만듦
- 컨테이너 IP는 다시 띄우면 바뀔 수 있으므로 **이름으로 통신**하는 것이 안전

### docker network ls

| 이름 | 드라이버 | 의미 |
|---|---|---|
| `04-compose_default` | bridge | 이번 Compose 프로젝트 전용 네트워크 |
| `bridge` | bridge | `docker run` 기본 네트워크 |
| `host` | host | 호스트 네트워크를 그대로 사용 |
| `none` | null | 네트워크 없음 |

### 컨테이너 이름 규칙

`04-compose-web-1` = **프로젝트명(폴더명) - 서비스명 - 번호**

### down과 down -v

```
docker compose down     → [+] down 3/3  (컨테이너 2개 + 네트워크)
docker compose down -v  → [+] down 4/4  (컨테이너 2개 + 네트워크 + 볼륨)
```

| 명령 | 방문 횟수 |
|---|---|
| `down` 후 `up` | **유지** |
| `down -v` 후 `up` | **초기화** |

- 방문 횟수는 컨테이너가 아니라 **`redis-data` 볼륨**에 저장됨
- `down`은 볼륨을 남기므로 새 Redis 컨테이너가 같은 볼륨에서 기존 데이터를 읽음
- `down -v`는 DB 데이터를 통째로 지우는 명령이라 실무에서는 매우 주의해서 사용

## 트러블슈팅

### web 컨테이너만 종료에 항상 10초 걸림

```
Container 04-compose-web-1   Removed   10.3s
Container 04-compose-redis-1 Removed    0.3s
```

- **원인**: Docker는 컨테이너를 멈출 때 PID 1에 **SIGTERM**을 보내고 10초 기다린 뒤 **SIGKILL**로 강제 종료한다. Redis는 SIGTERM을 받으면 저장 후 바로 종료하지만, PID 1로 실행된 Flask 개발 서버는 SIGTERM을 처리하지 않아 10초 후 강제 종료됨
- **영향**: 강제 종료 시 처리 중이던 요청이 끊기거나 데이터가 깨질 수 있음
- **해결 방법**: `web` 서비스에 `init: true` 추가
  → PID 1 자리에 신호를 제대로 전달하는 작은 init 프로세스(tini)를 둠

```yaml
  web:
    build: .
    init: true
```

- 참고: 실습 PC의 다른 컨테이너 COMMAND가 `tini -- python ...`이었던 것도 같은 문제를 같은 방법으로 해결한 것
