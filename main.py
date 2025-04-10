import os
import sys
import json
import git
from git import Repo
from dotenv import load_dotenv
import requests
import logging
from mcp.server.fastmcp import FastMCP

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# 환경 변수에서 저장소 경로 가져오기
REPO_PATH = os.getenv('GIT_REPO_PATH')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

logger.info("GIT-MCP-SERVER 시작")
logger.info(f"저장소 경로: {REPO_PATH}")

# MCP 서버 생성 (stdio 모드)
mcp = FastMCP(
    name="GitMCPServer",
    mode="stdio",
    version="1.0.0",
    description="Git 작업을 위한 MCP 서버"
)

@mcp.tool()
def get_repo_status() -> dict:
    """저장소 상태 조회"""
    try:
        logger.info("저장소 상태 조회 시작")
        repo = Repo(REPO_PATH)
        result = {
            "current_branch": repo.active_branch.name,
            "is_dirty": repo.is_dirty(),
            "untracked_files": repo.untracked_files,
            "modified_files": [item.a_path for item in repo.index.diff(None)],
            "staged_files": [item.a_path for item in repo.index.diff('HEAD')]
        }
        logger.info(f"저장소 상태: {result}")
        return result
    except Exception as e:
        logger.error(f"저장소 상태 조회 중 오류 발생: {str(e)}")
        raise

@mcp.tool()
def commit_changes(message: str, files: list = None) -> str:
    """변경사항 커밋"""
    try:
        logger.info(f"커밋 시작 - 메시지: {message}, 파일: {files}")
        repo = Repo(REPO_PATH)
        
        if files:
            # 파일 경로를 절대 경로로 변환
            absolute_files = [os.path.join(REPO_PATH, file) for file in files]
            logger.debug(f"절대 경로로 변환된 파일 목록: {absolute_files}")
            
            # 각 파일에 대해 존재 여부 확인
            for file_path in absolute_files:
                if os.path.exists(file_path):
                    # 파일이 존재하면 추가
                    logger.debug(f"파일 추가: {file_path}")
                    repo.index.add([file_path])
                else:
                    # 파일이 존재하지 않으면 삭제로 처리
                    relative_path = os.path.relpath(file_path, REPO_PATH)
                    logger.debug(f"파일 삭제: {relative_path}")
                    repo.index.remove([relative_path], working_tree=True)
        else:
            # 모든 변경사항 추가
            logger.debug("모든 변경사항 추가")
            repo.index.add('*')
            repo.git.add('-A')
            
        commit = repo.index.commit(message)
        logger.info(f"커밋 완료: {commit.hexsha}")
        return "Changes committed successfully"
    except Exception as e:
        logger.error(f"커밋 중 오류 발생: {str(e)}")
        raise

@mcp.tool()
def push_changes(remote: str = 'origin', branch: str = None):
    """변경사항 푸시"""
    try:
        repo = Repo(REPO_PATH)
        if not branch:
            branch = repo.active_branch.name
        origin = repo.remote(remote)
        origin.push(branch)
        return f"Changes pushed to {remote}/{branch}"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def pull_changes(remote='origin', branch=None):
    """변경사항 풀"""
    try:
        repo = Repo(REPO_PATH)
        if not branch:
            branch = repo.active_branch.name
        origin = repo.remote(remote)
        origin.pull(branch)
        return f"Changes pulled from {remote}/{branch}"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def create_branch(branch_name):
    """새 브랜치 생성"""
    try:
        repo = Repo(REPO_PATH)
        current = repo.active_branch
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()
        return f"Created and switched to branch {branch_name}"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def switch_branch(branch_name):
    """브랜치 전환"""
    try:
        repo = Repo(REPO_PATH)
        repo.heads[branch_name].checkout()
        return f"Switched to branch {branch_name}"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def merge_branch(source_branch):
    """브랜치 병합"""
    try:
        repo = Repo(REPO_PATH)
        current = repo.active_branch
        repo.git.merge(source_branch)
        return f"Merged {source_branch} into {current.name}"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def get_commit_history(limit=10):
    """커밋 히스토리 조회"""
    try:
        repo = Repo(REPO_PATH)
        commits = list(repo.iter_commits('HEAD', max_count=limit))
        return [{
            "hash": commit.hexsha,
            "message": commit.message,
            "author": commit.author.name,
            "date": commit.authored_datetime.isoformat()
        } for commit in commits]
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def get_branch_info():
    """브랜치 정보 조회"""
    try:
        repo = Repo(REPO_PATH)
        branches = [branch.name for branch in repo.heads]
        current = repo.active_branch.name
        return {
            "current": current,
            "all_branches": branches
        }
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def get_diff_stats():
    """변경사항 통계 조회"""
    try:
        repo = Repo(REPO_PATH)
        stats = repo.git.diff('--stat')
        return {"stats": stats}
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def create_tag(tag_name, message=None, commit_hash=None):
    """태그 생성"""
    try:
        repo = Repo(REPO_PATH)
        if commit_hash:
            commit = repo.commit(commit_hash)
        else:
            commit = repo.head.commit
            
        tag = repo.create_tag(tag_name, ref=commit, message=message)
        return f"Created tag {tag_name}"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def list_tags():
    """태그 목록 조회"""
    try:
        repo = Repo(REPO_PATH)
        tags = [tag.name for tag in repo.tags]
        return {"tags": tags}
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def delete_tag(tag_name, remote=False):
    """태그 삭제"""
    try:
        repo = Repo(REPO_PATH)
        repo.delete_tag(tag_name)
        if remote:
            repo.git.push('origin', f':refs/tags/{tag_name}')
        return f"Deleted tag {tag_name}"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def list_remotes():
    """원격 저장소 목록 조회"""
    try:
        repo = Repo(REPO_PATH)
        remotes = [remote.name for remote in repo.remotes]
        return {"remotes": remotes}
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def add_remote(name, url):
    """원격 저장소 추가"""
    try:
        repo = Repo(REPO_PATH)
        repo.create_remote(name, url)
        return f"Added remote {name}"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def remove_remote(name):
    """원격 저장소 제거"""
    try:
        repo = Repo(REPO_PATH)
        repo.delete_remote(name)
        return f"Removed remote {name}"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def set_remote_url(name, url):
    """원격 저장소 URL 변경"""
    try:
        repo = Repo(REPO_PATH)
        remote = repo.remote(name)
        remote.set_url(url)
        return f"Updated remote {name} URL"
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def create_pull_request(title, body, head, base='main', repo_owner=None, repo_name=None):
    """풀 리퀘스트 생성"""
    try:
        if not GITHUB_TOKEN:
            raise Exception("GitHub token not configured")
            
        if not repo_owner or not repo_name:
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                raise Exception("Could not determine repository owner and name")

        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'title': title,
            'body': body,
            'head': head,
            'base': base
        }
        
        response = requests.post(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls',
            headers=headers,
            json=data
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(response.json().get('message', 'Failed to create pull request'))
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def list_pull_requests(state='open', repo_owner=None, repo_name=None):
    """풀 리퀘스트 목록 조회"""
    try:
        if not GITHUB_TOKEN:
            raise Exception("GitHub token not configured")
            
        if not repo_owner or not repo_name:
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                raise Exception("Could not determine repository owner and name")

        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls',
            headers=headers,
            params={'state': state}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.json().get('message', 'Failed to list pull requests'))
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def get_pull_request(pull_number, repo_owner=None, repo_name=None):
    """풀 리퀘스트 상세 조회"""
    try:
        if not GITHUB_TOKEN:
            raise Exception("GitHub token not configured")
            
        if not repo_owner or not repo_name:
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                raise Exception("Could not determine repository owner and name")

        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_number}',
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.json().get('message', 'Failed to get pull request'))
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def update_pull_request(pull_number, title=None, body=None, state=None, repo_owner=None, repo_name=None):
    """풀 리퀘스트 업데이트"""
    try:
        if not GITHUB_TOKEN:
            raise Exception("GitHub token not configured")
            
        if not repo_owner or not repo_name:
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                raise Exception("Could not determine repository owner and name")

        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {}
        if title is not None:
            data['title'] = title
        if body is not None:
            data['body'] = body
        if state is not None:
            data['state'] = state
            
        response = requests.patch(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_number}',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.json().get('message', 'Failed to update pull request'))
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def merge_pull_request(pull_number, merge_method='merge', commit_title=None, commit_message=None, repo_owner=None, repo_name=None):
    """풀 리퀘스트 병합"""
    try:
        if not GITHUB_TOKEN:
            raise Exception("GitHub token not configured")
            
        if not repo_owner or not repo_name:
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                raise Exception("Could not determine repository owner and name")

        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'merge_method': merge_method
        }
        if commit_title:
            data['commit_title'] = commit_title
        if commit_message:
            data['commit_message'] = commit_message
            
        response = requests.put(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_number}/merge',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.json().get('message', 'Failed to merge pull request'))
    except Exception as e:
        raise Exception(str(e))

def process_command(command_data):
    """명령어 처리"""
    try:
        if not isinstance(command_data, dict):
            raise Exception("Invalid request format")
            
        jsonrpc = command_data.get('jsonrpc')
        if jsonrpc != '2.0':
            raise Exception("Invalid JSON-RPC version")
            
        method = command_data.get('method')
        if not method:
            raise Exception("Method is required")
            
        params = command_data.get('params', {})
        request_id = command_data.get('id')
        
        result = None
        
        if method == 'get_repo_status':
            result = get_repo_status()
        elif method == 'commit_changes':
            result = commit_changes(params.get('message'), params.get('files'))
        elif method == 'push_changes':
            result = push_changes(params.get('remote'), params.get('branch'))
        elif method == 'pull_changes':
            result = pull_changes(params.get('remote'), params.get('branch'))
        elif method == 'create_branch':
            result = create_branch(params.get('branch_name'))
        elif method == 'switch_branch':
            result = switch_branch(params.get('branch_name'))
        elif method == 'merge_branch':
            result = merge_branch(params.get('source_branch'))
        elif method == 'get_commit_history':
            result = get_commit_history(params.get('limit'))
        elif method == 'get_branch_info':
            result = get_branch_info()
        elif method == 'get_diff_stats':
            result = get_diff_stats()
        elif method == 'create_tag':
            result = create_tag(params.get('tag_name'), params.get('message'), params.get('commit_hash'))
        elif method == 'list_tags':
            result = list_tags()
        elif method == 'delete_tag':
            result = delete_tag(params.get('tag_name'), params.get('remote'))
        elif method == 'list_remotes':
            result = list_remotes()
        elif method == 'add_remote':
            result = add_remote(params.get('name'), params.get('url'))
        elif method == 'remove_remote':
            result = remove_remote(params.get('name'))
        elif method == 'set_remote_url':
            result = set_remote_url(params.get('name'), params.get('url'))
        elif method == 'create_pull_request':
            result = create_pull_request(
                params.get('title'),
                params.get('body'),
                params.get('head'),
                params.get('base'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        elif method == 'list_pull_requests':
            result = list_pull_requests(
                params.get('state'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        elif method == 'get_pull_request':
            result = get_pull_request(
                params.get('pull_number'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        elif method == 'update_pull_request':
            result = update_pull_request(
                params.get('pull_number'),
                params.get('title'),
                params.get('body'),
                params.get('state'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        elif method == 'merge_pull_request':
            result = merge_pull_request(
                params.get('pull_number'),
                params.get('merge_method'),
                params.get('commit_title'),
                params.get('commit_message'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        else:
            raise Exception(f"Unknown method: {method}")
            
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id if 'request_id' in locals() else None,
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }

def main():
    """메인 함수"""
    try:
        # 저장소 경로 확인
        if not REPO_PATH:
            logger.error("GIT_REPO_PATH가 설정되지 않음")
            sys.exit(1)
            
        # 저장소 경로가 존재하는지 확인
        if not os.path.exists(REPO_PATH):
            logger.error(f"저장소 경로가 존재하지 않음: {REPO_PATH}")
            sys.exit(1)
            
        # 저장소가 Git 저장소인지 확인
        try:
            Repo(REPO_PATH)
            logger.info("Git 저장소 확인 완료")
        except git.InvalidGitRepositoryError:
            logger.error(f"유효하지 않은 Git 저장소: {REPO_PATH}")
            sys.exit(1)
            
        logger.info("MCP 서버 실행")
        mcp.run()
    except Exception as e:
        logger.error(f"서버 실행 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 