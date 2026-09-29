# 03. Dockerfile로 나만의 이미지 만들기

## 실습 목표

Flask 웹앱을 Dockerfile로 이미지화하고, 코드 수정 후 새 버전으로 교체한다.

## 파일 구성

```
03-dockerfile/
├─ Dockerfile
├─ .dockerignore
├─ app.py
└─ requirements.txt
```

## Dockerfile 해설

```dockerfile
FROM python:3.12-slim                                # 기반 이미지 (Python이 설치된 가벼운 리눅스)
WORKDIR /app                                         # 컨테이너 안 작업 폴더
COPY requirements.txt .                              # 라이브러리 목록만 먼저 복사
RUN pip install --no-cache-dir -r requirements.txt   # 빌드 중에 Flask 설치
COPY app.py .                                        # 앱 코드 복사
EXPOSE 5000                                          # 이 앱이 쓰는 포트 (문서용 메모)
CMD ["python", "app.py"]                             # 컨테이너 실행 시 동작할 명령 (PID 1)
```

| 명령 | 동작 시점 |
|---|---|
| `RUN` | 이미지를 **빌드할 때** |
| `CMD` | 컨테이너를 **실행할 때** |

- `EXPOSE`는 메모일 뿐, 실제로 포트를 여는 건 `docker run -p`
- `app.py`에서 `host="0.0.0.0"`이 필요한 이유: 기본값(127.0.0.1)이면 컨테이너 자기 자신에서 오는 요청만 받아서, 포트 매핑을 해도 외부(브라우저)에서 접속 불가

## 실행한 명령어

```powershell
docker build -t myapp:1.0 .                          # 현재 폴더(.)를 재료로 이미지 빌드
docker images                                        # 이미지 목록 확인
docker run -d -p 5000:5000 --name myapp myapp:1.0    # 실행

# app.py 수정 후
docker build -t myapp:1.1 .                          # 새 버전 빌드
docker rm -f myapp                                   # 기존 컨테이너 삭제
docker run -d -p 5000:5000 --name myapp myapp:1.1    # 새 버전으로 교체
```

## 관찰한 것

- 브라우저에 표시된 `container: 41a9c1be78d6`이 컨테이너 ID 앞 12자리와 같음
  → 컨테이너 안에서 앱이 보는 호스트 이름 = 컨테이너 ID
- 빌드 로그의 `[1/5]` ~ `[5/5]` → Dockerfile 명령 하나하나가 단계. `EXPOSE`, `CMD`는 파일을 바꾸지 않는 설정이라 번호가 없음
- `FROM` 단계에서 `sha256:...` 3개를 다운로드 → 기반 이미지도 여러 레이어로 구성됨
- `docker images`의 DISK USAGE(198MB)와 CONTENT SIZE(48.2MB) → 압축 해제 후 크기와 압축된 크기

## 레이어 캐시와 Dockerfile 순서

Docker는 단계마다 재료가 지난번과 같으면 결과를 재사용한다(`CACHED`). 단, **한 단계가 바뀌면 그 아래 단계는 모두 다시 실행**된다.

`app.py`만 수정했을 때:

**requirements를 먼저 복사한 경우 (현재 방식)**
```
COPY requirements.txt .   → CACHED
RUN pip install ...       → CACHED
COPY app.py .             → 다시 실행 (0초)
```

**한꺼번에 복사한 경우**
```
COPY . .                  → 다시 실행
RUN pip install ...       → 다시 실행 (패키지가 많으면 수 분)
```

→ **잘 안 바뀌는 것은 위에, 자주 바뀌는 것은 아래에** 배치한다.
`requirements.txt`가 바뀌면 그때만 `pip install`이 다시 실행된다.

## 태그와 버전 관리

- 태그는 이미지의 이름표. 같은 태그로 다시 빌드하면 이름표가 새 이미지로 옮겨 감
- 내용이 같으면 모든 단계가 캐시되어 **같은 이미지 ID**에 태그만 두 개 붙음
- 이름표를 모두 잃은 이미지는 `<none>`(dangling)으로 남음 → `docker image prune`으로 정리
- 실무 원칙: **배포한 버전 태그는 덮어쓰지 않고** 새 번호를 붙임. 예외는 계속 옮겨 다니는 `latest`
- 이전 버전 이미지가 남아 있으므로 문제가 생기면 바로 되돌릴 수 있음

## 트러블슈팅

### 메모장으로 Dockerfile 만들 때 .txt가 붙는 문제
- **원인**: 메모장은 확장자 없는 새 파일을 저장할 때 `.txt`를 붙일 수 있음
- **해결**: `New-Item app.py, requirements.txt, Dockerfile`로 빈 파일을 먼저 만든 뒤 메모장으로 열기
