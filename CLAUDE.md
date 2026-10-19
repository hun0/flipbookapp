# 플립북 (Flipbook) — 작업 인계 메모

프레임 단위 애니메이션 드로잉 앱. 안드로이드 폰·태블릿(갤럭시 + S펜)이 주 사용 환경이고, PC(윈도우)에서도 쓴다.
사용자는 게임 VFX 아티스트라서 이펙트(검은 배경, 글로우, 스프라이트 시트, 투명 배경 내보내기) 작업 흐름이 중요하다.
UI 문구는 전부 한국어로 쓴다.

## 저장소 구조
- `www/index.html` — 앱 전체. HTML/CSS/JS가 한 파일에 다 들어 있다. **기능 수정은 거의 항상 이 파일만 고친다.**
- `www/jszip.min.js` — 빌드할 때 `npm run prep`이 node_modules에서 복사한다(커밋하지 않음).
- `electron/main.js` — 윈도우 앱 껍데기(Electron).
- `capacitor.config.json` — 안드로이드 앱 설정(Capacitor 6, appId `com.hun0fx.flipbook`).
- `package.json` — Capacitor·Electron·electron-builder 설정, 스크립트(`prep`, `desktop`, `build:win`, `build:android`).
- `.github/workflows/build.yml` — main에 push하면 APK·EXE 자동 빌드.

## 빌드·배포
- main에 push → Actions가 `android`(ubuntu) 다음 `windows` 작업을 돌린다. 빌드마다 `build-<번호>` 릴리스가 자동으로 생기고 `Flipbook.apk`와 EXE가 붙는다(폰에서는 Releases 페이지에서 바로 받는다). Artifacts에도 같은 파일이 있다.
- Claude 원격 세션에서는 git push와 `gh api`(읽기, 릴리스 자산 다운로드, `gh run cancel`)는 되지만 태그 push·API 쓰기·Artifacts zip 다운로드는 프록시가 막는다. 그래서 APK는 `build-<번호>` 릴리스 자산으로 받는다.
- `.gitignore`의 `/android/`·`/dist/`는 루트만 막는다(`icons/android/`는 커밋돼야 함).
- 안드로이드 서명: Secret `ANDROID_DEBUG_KEYSTORE`(디버그 키스토어 base64)를 `~/.android/debug.keystore`로 풀어서 매번 같은 키로 서명한다. 이게 빠지면 매 빌드 키가 달라져서 기존 앱 위에 설치가 안 된다("앱이 설치되지 않음").
- ubuntu 러너에는 Android SDK가 이미 깔려 있다. `android-actions/setup-android`는 쓰지 않는다(옛 `tools` 패키지를 받다가 실패했음).
- 윈도우: portable exe + NSIS 설치판. 코드 서명 없음.
- **수정할 때마다 `APP_VER` 문자열을 올린다.** 설정 창 아래에 표시돼서 새 빌드가 들어갔는지 사용자가 확인하는 용도다.

## 웹 버전과의 차이
원래 claude.ai 아티팩트(웹)로 만들었고, 앱용으로 아래만 다르다. 지금은 이 저장소의 `www/index.html`이 기준본이다.
- JSZip을 CDN 대신 로컬 `jszip.min.js`로 불러온다.
- `saveFile()`: Capacitor 네이티브면 `Filesystem.writeFile(CACHE)` 후 `Share.share`로 공유 창을 띄운다. Electron은 일반 다운로드(저장 창). 웹 아티팩트용 `window.claude.use('downloads')` 분기는 앱에서는 그냥 건너뛴다.

## 코드 구조 (www/index.html)
- 상태: `S`(도구·색·굵기·fps·어니언·배경·보정 등 설정), `layers`(id, name, visible, opacity, kind `raster|vector`, glow), `frames`(각 프레임 `{id, cv:{layerId: canvas}, vec:{layerId: [items]}}`), `curLayer`, 문서 크기 `W`,`H`.
- 래스터 레이어: 프레임×레이어마다 문서 해상도 캔버스 1장(그린 칸만 생성).
- 벡터 레이어: 아이템 배열. `line`(pts = [x,y,width,...], color, op, erase, 선택적으로 `bw` 원래 굵기) / `shape`(pts = [x,y,...], 올가미·자동 채우기, `af`가 붙으면 자동 채우기 결과). 배열은 불변으로 다룬다(바꿀 때 새 배열). `f.cv[lid]`는 문서 해상도 캐시이고 `rebuildVec()`로 다시 그린다.
- 화면 그리기: `render()` → 종이(배경) → 레퍼런스(뒤) → 어니언(뒤) → `drawFrameScreen()` → 어니언(앞) → 레퍼런스(앞) → 올가미 미리보기·끈 보정 가이드. 벡터 레이어는 `vecLayerScreen()`이 화면 해상도로 다시 그려서 확대해도 선명하다. 화면 변환은 `V {s, x, y, r}`(배율·이동·회전), `baseT()`, 역변환 `inv()`.
- 획 처리: `beginStroke` / `addPoints` / `endStroke`. 손떨림 보정 `S.stab`(`rope` 끈 당기기 · `lag` 따라가기 · `off`), 그린 뒤 다듬기 `smoothLine` / `smoothPoly`(`postK()`가 0이면 끔), 펜 끝 뾰족하게 `applyTaper`.
- 실행 취소: `undoStack` 항목 종류 `px`(ImageData before/after) · `vec`(배열 before/after) · `frames`(프레임 배열 구조) · `multi`(여러 개 묶음). 최대 40단계 + 메모리 약 160MB 상한(`trimUndo`). `syncUndo()`가 모든 편집 뒤에 불리고, 여기서 타임랩스 캡처도 건다.
- 자동 채우기: 래스터는 `autoFillRaster`(픽셀 플러드 + 선 아래 destination-over), 벡터는 `autoFillVector`(획 주변만 최대 4배 고해상도로 판독 → 외곽선 추적 `traceOutline` → 다듬기 → 벡터 shape). 끝이 거의 닫힌 획은 판정할 때만 가상 연결선을 긋는다.
- 프로젝트: 프로젝트마다 IndexedDB 데이터베이스가 따로 있다(첫 프로젝트는 `flipbook-anim`, 이후 `flipbook-anim-<id>`). 목록은 `flipbook-registry` DB의 `projects` 키(`{cur, list:[{id,name,db,w,h,updated,frames,thumb}]}`). 전환은 `switchProject()` → `flushSave()` → DB 닫기 → `enterProject()`(상태 초기화 후 load). 레퍼런스·타임랩스도 프로젝트별로 저장된다.
- 저장: 프로젝트 DB의 store `kv`. 키는 `meta`, `프레임id:레이어id`(래스터 PNG), `프레임id:레이어id:v`(벡터 JSON), `ref:*`·`refmeta`(레퍼런스), `tl:*`·`tlmeta`(타임랩스). 프로젝트 저장 정리 단계에서 `ref`·`tl`로 시작하는 키는 지우지 않는다. 설정 기본값을 바꿀 때는 `sv` 값으로 한 번만 이주(migration)한다.
- 대화창: 브라우저 `confirm` / `prompt`는 쓰지 않는다(웹 뷰어에서 막힘). `dialog()`, `askConfirm()`, `askText()`를 쓴다.

## 지금 있는 기능
- 도구: 브러시(펜·마커·올가미 채우기) / 지우개(지우개·올가미 지우개·획 지우개[벡터 전용]) / 채우기(버킷 + 닫힌 선 자동 채우기). 같은 아이콘을 한 번 더 누르면 서브 메뉴가 열린다.
- 레이어: 래스터·벡터, 표시·불투명도, 레이어 색(`tint`/`tintMode`: 단색 `replace` 또는 `multiply`, 원본 픽셀은 그대로 두고 그릴 때만 적용 — `applyTint`, `tintedDoc`, `layerSrc`), 레이어별 글로우(색 적용 후 그림 색 그대로 번짐, 더하기 합성), 래스터 변환.
- 프로젝트: 여러 작품을 앱 안에 따로 저장(상단 왼쪽 프로젝트 버튼). 새로 만들기·열기·이름 바꾸기·삭제.
- 프레임: 하단 썸네일 줄(문지르면 프레임 이동 + 가장자리 자동 스크롤), 왼쪽 세로 스크럽 휠(엄지용), 왼쪽/오른쪽에 새 프레임, 복제·삭제·이동, 재생(6~30fps).
- 어니언 스킨: 앞뒤 장 수, 위치(뒤·앞), 섞기(일반·곱하기), 진하기, 멀어질수록 흐려지는 정도.
- 레퍼런스: 이미지·GIF·스프라이트 시트·영상을 레이어와 별개로 깔고 이동·크기 조절. 내보내기에는 포함되지 않는다.
- 타임랩스: 편집할 때마다 한 컷씩 기록 → 15/30/60초 영상으로 저장.
- 내보내기: 스프라이트 시트 PNG, PNG 시퀀스 ZIP(레이어별 폴더 / 레이어별+합친 그림 / 합친 그림만 — `compLayerAt`로 레이어 하나씩 렌더), MP4/WebM, Krita `.kra`(`exportKra`: 레이어마다 paintlayer 하나, 모든 프레임을 raster 키프레임으로 — 타일 형식 VERSION 2, 64×64 BGRA, raw 플래그 0으로 저장, 레이어 색·글로우는 픽셀에 굽고 불투명도는 레이어 속성, 배경색은 맨 아래 잠긴 '배경' 레이어; Krita 5.2.2로 열어 프레임·색 확인함). 파일 이름 앞에 프로젝트 이름이 붙는다. 배경 투명 또는 배경색 포함. 벡터는 200·400% 고해상도로 내보내도 선명하다.
- 정사각 크롭 + 256/512/1024 해상도 맞추기.
- 입력: 두 손가락 확대·이동·회전, 두 손가락 탭 실행 취소, 세 손가락 탭 브러시↔지우개, 팜 리젝션(넓은 접촉, 펜 직후 터치 무시), S펜 버튼(펜↔지우개 전환 / 누르는 동안 지우개 / 프레임 넘기기).
- 기본값: 검은 배경, 흰 펜.

## 알려진 문제·제약
- 갤럭시는 S펜이 화면 위에 떠 있는 동안 손가락 터치를 시스템 단계에서 막는다. 앱에서 우회할 수 없다(펜을 1~2cm 이상 떨어뜨리면 터치가 된다).
- S펜 버튼 신호는 '에어 커맨드' 설정이나 기기에 따라 WebView까지 안 올 수 있다. 실기기 확인이 필요하다.
- 메모리 한계는 '프레임 수 × 레이어 수 × 캔버스 크기'다. 1280×720 기준으로 칸 하나에 약 3.7MB.
- 벡터 레이어 한 프레임에 획이 수백 개를 넘으면 확대·이동이 무거워질 수 있다.
- 아이패드(사파리 엔진) 대응은 아직이다: `ctx.filter` 블러(글로우)와 `ImageDecoder`(GIF 프레임 분리)를 사파리가 지원하지 않는다.

## 다음 할 일 후보
1. **작업 파일 백업·불러오기** (프로젝트 하나를 파일로 내보내고 다시 불러오기). 앱을 지우면 IndexedDB가 통째로 지워져서 모든 프로젝트가 사라지기 때문에 우선순위가 높다.
2. 프로젝트 복제.
3. 스플래시 화면. (앱 아이콘은 `icons/`에 있음 — `icons/parts.py`가 SVG를 만들고, 빌드 때 `icons/android/res`를 안드로이드 res에 복사, 윈도우는 `icons/icon.ico`)
4. 실기기(갤럭시)에서 S펜 버튼·팜 리젝션 동작 확인 후 조정.
5. 아이패드용 iOS 빌드(Capacitor iOS, 글로우·GIF 대체 구현).

## 작업 방식
- `www/index.html` 하나를 고치고, `APP_VER`를 올리고, 커밋해서 push하면 끝.
- push 후 Actions 결과(빨간 X)를 확인하고, 실패하면 로그를 보고 바로 고친다.
- 가능하면 헤드리스 브라우저(Playwright 등)로 그리기·채우기·내보내기를 돌려 보고 올린다.
