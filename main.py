import os
import sys
import json
import git
from git import Repo
from dotenv import load_dotenv
import requests

# .env 파일 로드
load_dotenv()

# 환경 변수에서 저장소 경로 가져오기
REPO_PATH = os.getenv('GIT_REPO_PATH')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def get_repo_status():
    """저장소 상태 조회"""
    try:
        repo = Repo(REPO_PATH)
        return {
            "status": "success",
            "data": {
                "current_branch": repo.active_branch.name,
                "is_dirty": repo.is_dirty(),
                "untracked_files": repo.untracked_files,
                "modified_files": [item.a_path for item in repo.index.diff(None)],
                "staged_files": [item.a_path for item in repo.index.diff('HEAD')]
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def commit_changes(message, files=None):
    """변경사항 커밋"""
    try:
        repo = Repo(REPO_PATH)
        
        if files:
            # 파일 경로를 절대 경로로 변환
            absolute_files = [os.path.join(REPO_PATH, file) for file in files]
            
            # 각 파일에 대해 존재 여부 확인
            for file_path in absolute_files:
                if os.path.exists(file_path):
                    # 파일이 존재하면 추가
                    repo.index.add([file_path])
                else:
                    # 파일이 존재하지 않으면 삭제로 처리
                    relative_path = os.path.relpath(file_path, REPO_PATH)
                    repo.index.remove([relative_path], working_tree=True)
        else:
            # 모든 변경사항 추가 (새 파일, 수정된 파일)
            repo.index.add('*')
            # 삭제된 파일 처리
            repo.git.add('-A')
            
        repo.index.commit(message)
        return {"status": "success", "message": "Changes committed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def push_changes(remote='origin', branch=None):
    """변경사항 푸시"""
    try:
        repo = Repo(REPO_PATH)
        if not branch:
            branch = repo.active_branch.name
        origin = repo.remote(remote)
        origin.push(branch)
        return {"status": "success", "message": f"Changes pushed to {remote}/{branch}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def pull_changes(remote='origin', branch=None):
    """변경사항 풀"""
    try:
        repo = Repo(REPO_PATH)
        if not branch:
            branch = repo.active_branch.name
        origin = repo.remote(remote)
        origin.pull(branch)
        return {"status": "success", "message": f"Changes pulled from {remote}/{branch}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_branch(branch_name):
    """새 브랜치 생성"""
    try:
        repo = Repo(REPO_PATH)
        current = repo.active_branch
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()
        return {"status": "success", "message": f"Created and switched to branch {branch_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def switch_branch(branch_name):
    """브랜치 전환"""
    try:
        repo = Repo(REPO_PATH)
        repo.heads[branch_name].checkout()
        return {"status": "success", "message": f"Switched to branch {branch_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def merge_branch(source_branch):
    """브랜치 병합"""
    try:
        repo = Repo(REPO_PATH)
        current = repo.active_branch
        repo.git.merge(source_branch)
        return {"status": "success", "message": f"Merged {source_branch} into {current.name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_commit_history(limit=10):
    """커밋 히스토리 조회"""
    try:
        repo = Repo(REPO_PATH)
        commits = list(repo.iter_commits('HEAD', max_count=limit))
        return {
            "status": "success",
            "data": [{
                "hash": commit.hexsha,
                "message": commit.message,
                "author": commit.author.name,
                "date": commit.authored_datetime.isoformat()
            } for commit in commits]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_branch_info():
    """브랜치 정보 조회"""
    try:
        repo = Repo(REPO_PATH)
        branches = [branch.name for branch in repo.heads]
        current = repo.active_branch.name
        return {
            "status": "success",
            "data": {
                "current": current,
                "all_branches": branches
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_diff_stats():
    """변경사항 통계 조회"""
    try:
        repo = Repo(REPO_PATH)
        stats = repo.git.diff('--stat')
        return {"status": "success", "data": {"stats": stats}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_tag(tag_name, message=None, commit_hash=None):
    """태그 생성"""
    try:
        repo = Repo(REPO_PATH)
        if commit_hash:
            commit = repo.commit(commit_hash)
        else:
            commit = repo.head.commit
            
        tag = repo.create_tag(tag_name, ref=commit, message=message)
        return {"status": "success", "message": f"Created tag {tag_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_tags():
    """태그 목록 조회"""
    try:
        repo = Repo(REPO_PATH)
        tags = [tag.name for tag in repo.tags]
        return {"status": "success", "data": {"tags": tags}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def delete_tag(tag_name, remote=False):
    """태그 삭제"""
    try:
        repo = Repo(REPO_PATH)
        repo.delete_tag(tag_name)
        if remote:
            repo.git.push('origin', f':refs/tags/{tag_name}')
        return {"status": "success", "message": f"Deleted tag {tag_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_remotes():
    """원격 저장소 목록 조회"""
    try:
        repo = Repo(REPO_PATH)
        remotes = [remote.name for remote in repo.remotes]
        return {"status": "success", "data": {"remotes": remotes}}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def add_remote(name, url):
    """원격 저장소 추가"""
    try:
        repo = Repo(REPO_PATH)
        repo.create_remote(name, url)
        return {"status": "success", "message": f"Added remote {name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def remove_remote(name):
    """원격 저장소 제거"""
    try:
        repo = Repo(REPO_PATH)
        repo.delete_remote(name)
        return {"status": "success", "message": f"Removed remote {name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def set_remote_url(name, url):
    """원격 저장소 URL 변경"""
    try:
        repo = Repo(REPO_PATH)
        remote = repo.remote(name)
        remote.set_url(url)
        return {"status": "success", "message": f"Updated remote {name} URL"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_pull_request(title, body, head, base='main', repo_owner=None, repo_name=None):
    """풀 리퀘스트 생성"""
    try:
        if not GITHUB_TOKEN:
            return {"status": "error", "message": "GitHub token not configured"}
            
        if not repo_owner or not repo_name:
            # 현재 저장소에서 owner와 repo 이름 추출
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                return {"status": "error", "message": "Could not determine repository owner and name"}

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
            return {"status": "success", "data": response.json()}
        else:
            return {"status": "error", "message": response.json().get('message', 'Failed to create pull request')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def list_pull_requests(state='open', repo_owner=None, repo_name=None):
    """풀 리퀘스트 목록 조회"""
    try:
        if not GITHUB_TOKEN:
            return {"status": "error", "message": "GitHub token not configured"}
            
        if not repo_owner or not repo_name:
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                return {"status": "error", "message": "Could not determine repository owner and name"}

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
            return {"status": "success", "data": response.json()}
        else:
            return {"status": "error", "message": response.json().get('message', 'Failed to list pull requests')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_pull_request(pull_number, repo_owner=None, repo_name=None):
    """풀 리퀘스트 상세 조회"""
    try:
        if not GITHUB_TOKEN:
            return {"status": "error", "message": "GitHub token not configured"}
            
        if not repo_owner or not repo_name:
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                return {"status": "error", "message": "Could not determine repository owner and name"}

        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(
            f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_number}',
            headers=headers
        )
        
        if response.status_code == 200:
            return {"status": "success", "data": response.json()}
        else:
            return {"status": "error", "message": response.json().get('message', 'Failed to get pull request')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def update_pull_request(pull_number, title=None, body=None, state=None, repo_owner=None, repo_name=None):
    """풀 리퀘스트 업데이트"""
    try:
        if not GITHUB_TOKEN:
            return {"status": "error", "message": "GitHub token not configured"}
            
        if not repo_owner or not repo_name:
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                return {"status": "error", "message": "Could not determine repository owner and name"}

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
            return {"status": "success", "data": response.json()}
        else:
            return {"status": "error", "message": response.json().get('message', 'Failed to update pull request')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def merge_pull_request(pull_number, merge_method='merge', commit_title=None, commit_message=None, repo_owner=None, repo_name=None):
    """풀 리퀘스트 병합"""
    try:
        if not GITHUB_TOKEN:
            return {"status": "error", "message": "GitHub token not configured"}
            
        if not repo_owner or not repo_name:
            repo = Repo(REPO_PATH)
            origin_url = repo.remote('origin').url
            if origin_url.startswith('https://github.com/'):
                parts = origin_url.replace('https://github.com/', '').replace('.git', '').split('/')
                repo_owner, repo_name = parts[0], parts[1]
            else:
                return {"status": "error", "message": "Could not determine repository owner and name"}

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
            return {"status": "success", "data": response.json()}
        else:
            return {"status": "error", "message": response.json().get('message', 'Failed to merge pull request')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_command(command_data):
    """명령어 처리"""
    try:
        command = command_data.get('command')
        params = command_data.get('params', {})
        
        if command == 'get_repo_status':
            return get_repo_status()
        elif command == 'commit_changes':
            return commit_changes(params.get('message'), params.get('files'))
        elif command == 'push_changes':
            return push_changes(params.get('remote'), params.get('branch'))
        elif command == 'pull_changes':
            return pull_changes(params.get('remote'), params.get('branch'))
        elif command == 'create_branch':
            return create_branch(params.get('branch_name'))
        elif command == 'switch_branch':
            return switch_branch(params.get('branch_name'))
        elif command == 'merge_branch':
            return merge_branch(params.get('source_branch'))
        elif command == 'get_commit_history':
            return get_commit_history(params.get('limit'))
        elif command == 'get_branch_info':
            return get_branch_info()
        elif command == 'get_diff_stats':
            return get_diff_stats()
        elif command == 'create_tag':
            return create_tag(params.get('tag_name'), params.get('message'), params.get('commit_hash'))
        elif command == 'list_tags':
            return list_tags()
        elif command == 'delete_tag':
            return delete_tag(params.get('tag_name'), params.get('remote'))
        elif command == 'list_remotes':
            return list_remotes()
        elif command == 'add_remote':
            return add_remote(params.get('name'), params.get('url'))
        elif command == 'remove_remote':
            return remove_remote(params.get('name'))
        elif command == 'set_remote_url':
            return set_remote_url(params.get('name'), params.get('url'))
        elif command == 'create_pull_request':
            return create_pull_request(
                params.get('title'),
                params.get('body'),
                params.get('head'),
                params.get('base'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        elif command == 'list_pull_requests':
            return list_pull_requests(
                params.get('state'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        elif command == 'get_pull_request':
            return get_pull_request(
                params.get('pull_number'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        elif command == 'update_pull_request':
            return update_pull_request(
                params.get('pull_number'),
                params.get('title'),
                params.get('body'),
                params.get('state'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        elif command == 'merge_pull_request':
            return merge_pull_request(
                params.get('pull_number'),
                params.get('merge_method'),
                params.get('commit_title'),
                params.get('commit_message'),
                params.get('repo_owner'),
                params.get('repo_name')
            )
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    """메인 함수"""
    try:
        # 저장소 경로 확인
        if not REPO_PATH:
            print(json.dumps({"status": "error", "message": "GIT_REPO_PATH not set in environment variables"}))
            sys.exit(1)
            
        # 저장소 경로가 존재하는지 확인
        if not os.path.exists(REPO_PATH):
            print(json.dumps({"status": "error", "message": f"Repository path does not exist: {REPO_PATH}"}))
            sys.exit(1)
            
        # 저장소가 Git 저장소인지 확인
        try:
            Repo(REPO_PATH)
        except git.InvalidGitRepositoryError:
            print(json.dumps({"status": "error", "message": f"Not a valid Git repository: {REPO_PATH}"}))
            sys.exit(1)
            
        # 표준 입력에서 명령어 읽기
        for line in sys.stdin:
            try:
                command_data = json.loads(line.strip())
                result = process_command(command_data)
                print(json.dumps(result))
                sys.stdout.flush()
            except json.JSONDecodeError:
                print(json.dumps({"status": "error", "message": "Invalid JSON input"}))
                sys.stdout.flush()
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main() 