# 채널: GitHub

코드·오픈소스·기술 문서·이슈·릴리스의 본진. 공개 리포는 무설정으로 즉시 긁힌다.
([access-tiers.md](access-tiers.md) 참조)

## 긁는 순서

1. **`gh` CLI(가장 강력, 설치 시).**
   - 리포 검색: `gh search repos "키워드" --limit 20`
   - 코드 검색: `gh search code "함수명 language:python"`
   - 이슈/PR: `gh search issues "에러메시지"` / `gh issue list -R owner/repo`
   - 파일 읽기: `gh api repos/owner/repo/contents/경로 --jq .content | base64 -d`
2. **GitHub REST API(키 없이 공개, 무설정).** `WebFetch`로:
   - `https://api.github.com/search/repositories?q=키워드&sort=stars`
   - `https://api.github.com/repos/owner/repo` (스타·언어·설명)
   - `https://raw.githubusercontent.com/owner/repo/main/README.md` (README 원문)
3. **웹.** `WebSearch`로 `site:github.com [키워드]`, 릴리스 노트는 리포 페이지 `WebFetch`.

## 요령

- 라이브러리 조사: 스타·최근 커밋·이슈 활성도·README를 함께 봐 생존 여부를 판단한다.
- 에러 추격: 에러 메시지를 그대로 이슈 검색에 넣으면 해결책이 나온다.
- 비공개 리포·조직 전용은 인증이 필요하다. 우회하지 않고 보고한다.
