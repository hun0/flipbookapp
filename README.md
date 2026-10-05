# 플립북 (Flipbook)

프레임 애니메이션 드로잉 앱. GitHub에 올리면 **안드로이드 APK**와 **윈도우 EXE**가 자동으로 빌드돼요.

## 폴더 구성
- `www/index.html` — 앱 본체 (웹 버전과 같은 코드, 오프라인용으로 약간 수정)
- `electron/main.js` — 윈도우 앱 껍데기
- `capacitor.config.json` — 안드로이드 앱 설정
- `.github/workflows/build.yml` — 자동 빌드 설정

## 자동 빌드
1. GitHub에서 새 저장소(Repository)를 만들어요. 비공개(Private)도 돼요.
2. 이 폴더 안의 파일을 전부 올려요. `.github` 폴더도 꼭 포함돼야 해요.
3. 저장소의 **Actions** 탭에서 "Build APK & EXE"가 도는 걸 확인해요. 10~15분 정도 걸려요.
4. 끝나면 실행 기록을 눌러 아래 **Artifacts**에서 받아요.
   - `Flipbook-android` → `Flipbook.apk`
   - `Flipbook-windows` → `Flipbook-…-portable.exe`(설치 없이 실행), `Flipbook-…-setup.exe`(설치판)

## 폰에서 바로 받기 (릴리스)
`v1.0.0` 같은 태그를 만들어 올리면, 빌드 결과가 저장소의 **Releases**에 바로 붙어요.
Releases 페이지는 폰 브라우저에서도 바로 다운로드돼요.

## 코드 수정 후
`www/index.html`을 바꿔서 올리면(커밋) 다시 자동 빌드돼요.

## 참고
- APK는 디버그 서명이라 설치할 때 "출처를 알 수 없는 앱 설치"를 허용해야 해요. Play 스토어에 올리려면 정식 서명 키가 따로 필요해요.
- 윈도우 EXE는 코드 서명이 없어서 처음 실행할 때 SmartScreen 경고가 뜰 수 있어요. "추가 정보 → 실행"을 누르면 돼요.
- 앱 아이콘은 기본 아이콘이에요.
