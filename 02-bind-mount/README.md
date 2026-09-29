# 02. 컨테이너 데이터와 바인드 마운트

## 실습 목표

컨테이너를 삭제하면 내부 변경 사항이 사라지는 것을 확인하고, 바인드 마운트로 데이터를 컨테이너 바깥에 유지한다.

## 1. 컨테이너를 지우면 수정한 파일도 사라질까?

01에서 `echo`로 `index.html`을 수정한 뒤, 컨테이너를 삭제하고 다시 실행했다.

```powershell
docker rm -f my-nginx
docker run -d -p 8080:80 --name my-nginx nginx
```

**결과**: 수정한 페이지가 사라지고 원래의 "Welcome to nginx!"가 다시 나옴

**이유**: 이미지는 읽기 전용이고, 컨테이너는 이미지 위에 **얇은 쓰기 레이어**를 얹어 변경 사항을 저장한다. `rm`하면 이 쓰기 레이어도 함께 삭제되고, 새 컨테이너는 깨끗한 원본 이미지 위에 새 쓰기 레이어를 얹어 시작한다.

## 2. 바인드 마운트

```powershell
cd ~\docker-practice\02-bind-mount
docker run -d -p 8080:80 --name my-nginx -v "${PWD}\site:/usr/share/nginx/html" nginx
```

- `-v 호스트경로:컨테이너경로` (`-p`와 마찬가지로 왼쪽이 내 PC, 오른쪽이 컨테이너)
- `${PWD}`: PowerShell에서 현재 폴더 경로

### 확인한 것
1. 브라우저에 Windows 폴더의 `site/index.html` 내용이 표시됨
2. 메모장으로 `index.html`을 수정하고 저장하면 **컨테이너 재시작 없이** 바로 반영됨
3. 컨테이너를 삭제하고 다시 만들어도 수정한 내용이 그대로 남아 있음
4. 컨테이너 안에서 파일을 만들면 Windows 폴더에도 생김 → **양방향**

```powershell
docker exec my-nginx sh -c "echo '<h1>made inside container</h1>' > /usr/share/nginx/html/inside.html"
```

## 동작 원리

바인드 마운트는 파일을 **복사하는 것이 아니라 경로를 연결**하는 것이다. 컨테이너 안의 `/usr/share/nginx/html`로 들어가면 실제로는 Windows의 `site` 폴더로 통한다.

```
브라우저 → localhost:8080 → 컨테이너의 nginx
nginx: /usr/share/nginx/html/index.html 읽기
   ↓ (마운트 지점이라 경로가 연결됨)
Windows의 site\index.html 을 읽음
```

- nginx는 요청마다 파일을 새로 읽기 때문에 수정 즉시 반영됨
- 컨테이너를 지워도 사라지는 건 쓰기 레이어뿐이고, Windows 폴더는 컨테이너의 일부가 아니므로 남음
- 마운트하면 그 경로에 원래 있던 파일(`50x.html` 등)은 **삭제되는 게 아니라 가려짐**

Windows에서는 한 단계가 더 있다.

```
Windows 폴더 → (Docker Desktop 파일 공유) → WSL2 VM → (바인드 마운트) → 컨테이너
```

실제 리눅스 서버에서는 중간 단계 없이 서버 폴더가 컨테이너에 바로 연결된다.

## URL과 파일의 관계

| 브라우저 주소 | nginx가 읽는 파일 |
|---|---|
| `localhost:8080/` | `site/index.html` (경로가 비면 기본 파일) |
| `localhost:8080/inside.html` | `site/inside.html` |
| `localhost:8080/favicon.ico` | `site/favicon.ico` (없으면 404) |

## 실무에서의 데이터 관리

| 종류 | 예시 | 두는 곳 |
|---|---|---|
| 코드 | 앱 소스, 웹페이지 | 이미지 안 (Dockerfile) |
| 설정 | `nginx.conf` 등 | 바인드 마운트 또는 환경 변수 |
| 데이터 | DB 파일, 업로드 파일, 로그 | 볼륨 |

- `-v`는 여러 개 사용 가능하고, 폴더뿐 아니라 파일 하나만 연결할 수도 있음
- `:ro`를 붙이면 컨테이너는 읽기만 가능
- 경로 대신 이름을 쓰면(`-v nginx-logs:/var/log/nginx`) Docker가 관리하는 **볼륨**
- 옵션이 많아지면 **Docker Compose**로 YAML 파일에 정리해서 관리

## 유용한 확인 명령어

```powershell
docker diff my-nginx                                   # 이미지 대비 변경된 파일 (A 추가, C 변경, D 삭제)
docker inspect my-nginx --format "{{json .Mounts}}"    # 마운트 정보 (Source, Destination)
docker cp my-nginx:/usr/share/nginx/html/index.html .  # 컨테이너 파일을 호스트로 복사
```
