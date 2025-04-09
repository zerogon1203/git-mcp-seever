# GIT-MCP-SERVER

LLM Agent와 연동 가능한 Model Context Protocol (MCP) Stdio 서버입니다.

## 프로젝트 설명

이 프로젝트는 LLM Agent가 Git 관련 기능을 활용할 수 있도록 Python 기반의 Git 관련 기능들을 제공합니다.

## 주요 기능

- 저장소 상태 조회
- 커밋 생성 및 관리
- 푸시 / 풀
- 브랜치 생성 / 이동 / 병합
- 커밋 히스토리 조회
- 변경사항 통계
- 태그 관리
- 원격 저장소 관리
- 풀 리퀘스트 관리

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/git-mcp-server.git
cd git-mcp-server
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가합니다:
```
GIT_REPO_PATH=/path/to/your/git/repository
GITHUB_TOKEN=your_github_personal_access_token  # GitHub API 사용 시 필요
```

## MCP 설정

MCP 설정 파일에 다음과 같이 추가합니다:

```json
{
  "git-mcp-server": {
    "transport": "stdio",
    "command": "/path/to/your/venv/bin/python",
    "args": ["/path/to/your/git-mcp-server/main.py"],
    "env": {
      "GIT_REPO_PATH": "/path/to/your/git/repository",
      "GITHUB_TOKEN": "your_github_personal_access_token"
    }
  }
}
```

## 사용 방법

서버 실행:
```bash
python main.py
```

### 사용 가능한 명령어

1. 저장소 상태 조회
```json
{
    "command": "get_repo_status"
}
```

2. 변경사항 커밋
```json
{
    "command": "commit_changes",
    "params": {
        "message": "커밋 메시지",
        "files": ["file1.txt", "file2.txt"]  // 선택사항
    }
}
```

3. 변경사항 푸시
```json
{
    "command": "push_changes",
    "params": {
        "remote": "origin",  // 선택사항
        "branch": "main"     // 선택사항
    }
}
```

4. 변경사항 풀
```json
{
    "command": "pull_changes",
    "params": {
        "remote": "origin",  // 선택사항
        "branch": "main"     // 선택사항
    }
}
```

5. 브랜치 생성
```json
{
    "command": "create_branch",
    "params": {
        "branch_name": "feature/new-branch"
    }
}
```

6. 브랜치 전환
```json
{
    "command": "switch_branch",
    "params": {
        "branch_name": "feature/new-branch"
    }
}
```

7. 브랜치 병합
```json
{
    "command": "merge_branch",
    "params": {
        "source_branch": "feature/new-branch"
    }
}
```

8. 커밋 히스토리 조회
```json
{
    "command": "get_commit_history",
    "params": {
        "limit": 10  // 선택사항
    }
}
```

9. 브랜치 정보 조회
```json
{
    "command": "get_branch_info"
}
```

10. 변경사항 통계 조회
```json
{
    "command": "get_diff_stats"
}
```

11. 태그 생성
```json
{
    "command": "create_tag",
    "params": {
        "tag_name": "v1.0.0",
        "message": "릴리스 버전 1.0.0",  // 선택사항
        "commit_hash": "abc123"  // 선택사항
    }
}
```

12. 태그 목록 조회
```json
{
    "command": "list_tags"
}
```

13. 태그 삭제
```json
{
    "command": "delete_tag",
    "params": {
        "tag_name": "v1.0.0",
        "remote": true  // 선택사항, 원격 저장소에서도 삭제할지 여부
    }
}
```

14. 원격 저장소 목록 조회
```json
{
    "command": "list_remotes"
}
```

15. 원격 저장소 추가
```json
{
    "command": "add_remote",
    "params": {
        "name": "upstream",
        "url": "https://github.com/original/repo.git"
    }
}
```

16. 원격 저장소 제거
```json
{
    "command": "remove_remote",
    "params": {
        "name": "upstream"
    }
}
```

17. 원격 저장소 URL 변경
```json
{
    "command": "set_remote_url",
    "params": {
        "name": "origin",
        "url": "https://github.com/new/repo.git"
    }
}
```

18. 풀 리퀘스트 생성
```json
{
    "command": "create_pull_request",
    "params": {
        "title": "새로운 기능 추가",
        "body": "이 PR은 새로운 기능을 추가합니다.",
        "head": "feature/new-feature",
        "base": "main",  // 선택사항
        "repo_owner": "username",  // 선택사항
        "repo_name": "repo-name"  // 선택사항
    }
}
```

19. 풀 리퀘스트 목록 조회
```json
{
    "command": "list_pull_requests",
    "params": {
        "state": "open",  // 선택사항: open, closed, all
        "repo_owner": "username",  // 선택사항
        "repo_name": "repo-name"  // 선택사항
    }
}
```

20. 풀 리퀘스트 상세 조회
```json
{
    "command": "get_pull_request",
    "params": {
        "pull_number": 123,
        "repo_owner": "username",  // 선택사항
        "repo_name": "repo-name"  // 선택사항
    }
}
```

21. 풀 리퀘스트 업데이트
```json
{
    "command": "update_pull_request",
    "params": {
        "pull_number": 123,
        "title": "수정된 제목",  // 선택사항
        "body": "수정된 내용",  // 선택사항
        "state": "open",  // 선택사항: open, closed
        "repo_owner": "username",  // 선택사항
        "repo_name": "repo-name"  // 선택사항
    }
}
```

22. 풀 리퀘스트 병합
```json
{
    "command": "merge_pull_request",
    "params": {
        "pull_number": 123,
        "merge_method": "merge",  // 선택사항: merge, squash, rebase
        "commit_title": "병합 커밋 제목",  // 선택사항
        "commit_message": "병합 커밋 메시지",  // 선택사항
        "repo_owner": "username",  // 선택사항
        "repo_name": "repo-name"  // 선택사항
    }
}
```

## 라이선스

MIT License 