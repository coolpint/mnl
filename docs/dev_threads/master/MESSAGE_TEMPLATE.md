# Master 업데이트 메시지 템플릿

아래 형식을 그대로 복사해 `MASTER_INBOX.md`에 추가한다.

```md
## [OPEN][REQ-YYYYMMDD-XX] <짧은 제목>
- from: `Thread-<A|B|C|D|E|F>`
- date: `YYYY-MM-DD`
- type: `conflict | contract-change | policy-change | blocker`
- affected: `<파일/모듈/스레드>`
- summary: `<무엇이 충돌/변경인지>`
- options:
  1. `<옵션 1>`
  2. `<옵션 2>`
- recommendation: `<권장안 + 이유>`
- decision-needed-by: `YYYY-MM-DD`
- links: `<PR/문서/이슈>`
```

결정 후 master가 아래처럼 회신한다.

```md
## [DECIDED][M-XXX] <짧은 제목>
- decision-date: `YYYY-MM-DD`
- outcome: `<채택안>`
- rationale: `<근거>`
- applies-to: `<스레드/파일>`
- follow-ups:
  - [ ] `<후속 작업>`
```
