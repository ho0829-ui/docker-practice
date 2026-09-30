# Docker 기초 실습

Docker를 처음 접하면서 컨테이너 실행부터 나만의 이미지 빌드, 레지스트리 배포, Compose 구성까지 직접 실습한 기록입니다.
명령어뿐 아니라 **로그와 출력에서 관찰한 것**, **겪은 문제와 해결 과정**을 함께 정리했습니다.

## 실습 환경

| 항목 | 내용 |
|---|---|
| OS | Windows (PowerShell) |
| Docker | Docker Desktop (Client 29.6.2) |
| 엔진 실행 환경 | WSL2 리눅스 VM |

## 목차

| 단계 | 내용 | 핵심 개념 |
|---|---|---|
| [01-basic](./01-basic) | hello-world, nginx 실행, 로그 확인, 컨테이너 내부 접속 | 이미지와 컨테이너, 포트 매핑, PID 1 |
| [02-bind-mount](./02-bind-mount) | 컨테이너 삭제 시 데이터 소실 확인, 바인드 마운트 | 쓰기 레이어, 마운트 |
| [03-dockerfile](./03-dockerfile) | Flask 앱을 Dockerfile로 이미지화, 버전 관리 | 레이어 캐시, RUN과 CMD, 태그 |
| [03-dockerfile/registry.md](./03-dockerfile/registry.md) | 만든 이미지를 Docker Hub에 push, 삭제 후 pull | 레지스트리, 레이어 해시, Untagged와 Deleted |
| [04-compose](./04-compose) | Flask + Redis 방문자 카운터를 Compose로 구성 | 서비스 이름 DNS, 이름 있는 볼륨, SIGTERM |

## 핵심 개념 요약

- **이미지**: 앱과 실행 환경을 담은 읽기 전용 설계도
- **컨테이너**: 이미지를 실행한 실체. 이미지 위에 얇은 쓰기 레이어가 얹혀 있음
- **Dockerfile**: 이미지를 만드는 레시피
- **레지스트리**: 이미지를 올리고 내려받는 저장소 (예: Docker Hub)
- **Docker Compose**: 여러 컨테이너의 설정을 YAML 파일 하나로 정의하고 한 번에 실행하는 도구
- **컨테이너와 VM의 차이**: VM은 자기 커널을 가진 OS 전체를 부팅하고, 컨테이너는 호스트 커널을 공유하는 격리된 프로세스

## 사용한 명령어

### 컨테이너와 이미지

| 명령어 | 설명 |
|---|---|
| `docker version` | Client와 Server(엔진) 상태 확인 |
| `docker run` | 이미지로 새 컨테이너를 만들어 실행 |
| `docker ps` / `docker ps -a` | 실행 중인 컨테이너 / 종료된 것까지 전체 |
| `docker logs` | 컨테이너 출력 확인 |
| `docker exec -it <이름> bash` | 실행 중인 컨테이너 안에서 셸 열기 |
| `docker stop` / `docker start` | 컨테이너 중지 / 기존 컨테이너 다시 실행 |
| `docker rm -f` | 컨테이너 강제 중지 후 삭제 |
| `docker build -t <이름>:<태그> .` | Dockerfile로 이미지 빌드 |
| `docker images` | 이미지 목록 확인 |
| `docker rmi` | 이미지 이름표 제거 (마지막 이름표면 이미지 삭제) |

### 레지스트리

| 명령어 | 설명 |
|---|---|
| `docker login` / `docker logout` | Docker Hub 로그인 / 로그아웃 |
| `docker tag <원본> <사용자명>/<이름>:<태그>` | 레지스트리용 이름표 추가 |
| `docker push` | 이미지를 레지스트리에 업로드 |
| `docker pull` | 레지스트리에서 이미지 다운로드 |

### Compose

| 명령어 | 설명 |
|---|---|
| `docker compose up -d --build` | 이미지 빌드 후 모든 서비스 실행 |
| `docker compose ps` | 서비스 상태 확인 |
| `docker compose exec <서비스> <명령>` | 서비스 컨테이너 안에서 명령 실행 |
| `docker compose down` | 컨테이너와 네트워크 삭제 (볼륨은 유지) |
| `docker compose down -v` | 볼륨까지 삭제 (데이터 초기화) |
| `docker network ls` | Docker 네트워크 목록 |

## 다음 계획

- [x] Docker Hub에 이미지 `push` / `pull`
- [x] Docker Compose로 Flask + Redis 구성
- [x] 볼륨(named volume)으로 데이터 유지
- [ ] `init: true`로 web 컨테이너 종료 지연 문제 해결 확인
- [ ] Compose에 nginx를 앞단(리버스 프록시)으로 추가
