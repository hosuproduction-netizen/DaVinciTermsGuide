# 다빈치 가이드 (DaVinci Guide)

**프로그램 전환 + 검색 가능한 다빈치 리졸브 기능 사전**의 첫 번째 정적 웹사이트 시안입니다.

## 제공 기능
- Premiere Pro, CapCut, Final Cut Pro, VLLO의 **47개 기능 대응표** (각 프로그램에서 검색 가능)
- 한글 용어, 영문 기능명, 일상 표현을 찾아주는 **통합 검색**
- 기본 편집 · 영상 효과 · 자막·그래픽 · 색보정 · 오디오 · 내보내기 **카테고리 필터**
- **기능별 고유 URL 47개**와 정적 HTML 설명: 메뉴 위치, 사용 순서, 무료/Studio 여부, 용어 차이
- 제공된 5개 앱 아이콘을 사용한 **프로그램 선택 카드 / 사이트 로고·파비콘 / 상세 비교 아이콘**
- 스마트폰부터 데스크톱까지 반응형 디자인
- 외부 서버·DB 없이 작동하는 HTML/CSS/JavaScript 사이트

## 미리 보기

`index.html`을 더블클릭하면 웹사이트가 바로 열립니다. 오프라인에서도 검색과 메뉴 이동이 동작합니다.

개발용 서버로 보려면 이 디렉터리에서 다음을 실행해도 됩니다.

```bash
python3 -m http.server 8000
```

그런 다음 브라우저에서 `http://localhost:8000/`을 엽니다.

## 내용 수정

기능과 비교 용어의 원본 데이터는 `content/features.json`에 있습니다.

- `title`, `resolve`, `category`, `location`, `summary`, `steps`, `tip` = 다빈치 기능 설명
- `keywords` = 검색 별칭
- `maps.premiere`, `maps.capcut`, `maps.final-cut-pro`, `maps.vllo` = 기존 프로그램 대응 명칭
- `maps.*.status` = `유사` / `대체` / `차이 있음`
- `edition` = `무료` / `Studio` / `Studio 확인` / `효과별 확인`
- `related` = 다른 기능의 slug
- `source` = 가능하면 Blackmagic Design·Adobe·Apple 공식 자료 URL

JSON을 수정하면 **정적 페이지를 다시 생성해야** 반영됩니다.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build.py
```

## 검색엔진 등록 전에 꼭 할 일

개별 페이지의 검색 노출을 위해 내용이 담긴 **정적 HTML**을 생성합니다. 현재는 배포 도메인이 정해지지 않았으므로 잘못된 주소가 들어가지 않도록 `canonical` 및 `sitemap.xml`은 생성하지 않았습니다. 배포하려는 정확한 주소(하위 경로 포함)를 지정해 빌드하면 자동으로 생성됩니다.

```bash
# 예: 실제 확정된 주소로 교체
SITE_URL=https://your-real-domain.example/davinci-guide/ python3 scripts/build.py
```

이렇게 하면 모든 개별 기능 페이지에 절대경로 canonical/OG URL이 추가되고 `sitemap.xml`이 만들어집니다. 이후 검색엔진 도구에 해당 사이트맵을 등록할 수 있습니다. **검색 노출·순위는 보장되지 않으며**, 내용의 정확성과 페이지 품질·수집 정책 등의 영향을 받습니다.

GitHub Pages 프로젝트 저장소를 이용할 경우 `https://계정.github.io/저장소명/`처럼 하위 경로를 포함하여 `SITE_URL`을 입력합니다. 단, `robots.txt`는 검색엔진이 도메인 루트에서 찾으므로 프로젝트 하위 폴더에 업로드한 robots.txt만으로 루트 정책을 바꿀 수 없습니다.

## 편집 가이드 정보의 정확성

- 기준 버전: **DaVinci Resolve 21.1**. 환경·언어 설정·업데이트에 따라 메뉴 위치가 달라질 수 있습니다.
- 이 사이트는 **동일 / 호환 여부 판정표가 아닌 작업 목적별 전환 가이드**입니다. `유사` 기능도 효과·구현 원리·고급 옵션이 다를 수 있습니다.
- 특히 VLLO, CapCut처럼 모바일·PC·업데이트별 UI 차이가 큰 앱은 일상적인 작업 이름을 비교 용어로 제시했습니다. 배포 전 실제 앱 화면으로 메뉴명을 검수하면 좋습니다.
- Studio 지원 범위가 확실하지 않은 기능은 `확인`으로 표기했습니다.
- `블하TV` 영상 링크는 검증된 영상이 아직 지정되지 않아 페이지에 넣지 않았습니다. `feature` 데이터에 영상 필드를 추가해 쉽게 확장할 수 있습니다.

## 구조

```text
index.html                 # 첫 화면
programs/{slug}/index.html # 프로그램별 기능 비교
features/{slug}/index.html # 검색엔진용 개별 기능 정적 페이지
dictionary/index.html      # 다빈치 기능 사전
assets/style.css           # 기본 스타일
assets/icons.css           # 앱 아이콘 전용 스타일
assets/icons/*.webp        # 사용자 제공 프로그램 아이콘(화면용)
assets/icons/*.png         # 사이트 파비콘·홈 화면 아이콘
assets/app.js              # 검색·필터·전환
assets/data.js             # JSON에서 생성한 검색 데이터
content/features.json      # 유일한 콘텐츠 원본
templates/*.html           # HTML 템플릿
scripts/build.py           # 정적 페이지 생성기
```

블하TV 및 강의용 참고 자료 시안입니다. 정식 공개 전 용어와 각 기능의 작동 여부를 확인하여 업데이트하세요.

## 프로그램 아이콘 관리

`assets/icons/`에는 사용자가 제공한 Premiere Pro, CapCut, Final Cut Pro, VLLO, DaVinci Resolve 로고를 웹사이트에 맞춰 최적화한 파일을 넣었습니다. **카드와 상세페이지 모두 같은 자산**을 사용합니다. 로고 크기는 `assets/icons.css`에서 쉽게 조절할 수 있습니다. VLLO는 여백이 큰 원본의 상징 부분만 잘라 투명 배경으로 저장해 작은 카드에서도 알아보기 쉽도록 했습니다. 제3자 상표·아이콘은 각 소프트웨어 업체에 귀속됩니다.
