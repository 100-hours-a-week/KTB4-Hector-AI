import click
import json
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_DB = os.path.join(BASE_DIR, "users.json")

def load_users():
    #사용자 목록 불러오기
    if os.path.exists(USERS_DB):
        try:
            with open(USERS_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return {}
    return {}

def save_users(users):
    #사용자 정보 목록 저장
    with open(USERS_DB, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def load_data(db_file):
    #특정 사용자의 단어장 불러오기
    if os.path.exists(db_file):
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []
    return []

def save_data(db_file, word_list):
    #특정 사용자의 단어장 데이터 저장
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(word_list, f, ensure_ascii=False, indent=4)
#단어 저장 로직
def add_word(db_file):
    word_list = load_data(db_file)
    print("\n--- [단어 등록] ---")
    word = input("영어 단어를 입력하세요: ").strip()
    meaning = input("뜻을 입력하세요: ").strip()
    
    if word and meaning:
        word_list.append({"word": word, "meaning": meaning})
        save_data(db_file, word_list)
        print(f" '{word}' 등록 완료!")
    else:
        print("단어와 뜻을 모두 입력해야 합니다.")

def run_quiz(db_file):
    word_list = load_data(db_file)
    if not word_list:
        print("\n 등록된 단어가 하나도 없네요!")
        print("먼저 1번 메뉴를 통해 단어를 등록해주세요.")
        return

    print("\n--- [영단어 퀴즈] (종료하려면 'q' 입력) ---")
    quiz_data = word_list.copy()
    random.shuffle(quiz_data)
    
    score = 0
    for item in quiz_data:
        answer = input(f"'{item['meaning']}' -> 영어로? ").strip().lower()
        if answer == 'q': break
        
        if answer == item['word'].lower():
            print("정답입니다!")
            score += 1
        else:
            print(f"틀렸습니다. 정답은 '{item['word']}'입니다. ")
            
    print(f"\n 퀴즈 종료! 맞춘 개수: {score}/{len(quiz_data)}")

def interactive_menu(name, db_file):
    #비밀번호 확인 후 진입
    while True:
        word_list = load_data(db_file)
        
        print(f"\n======= {name}님의 영단어 마스터 =======")
        print(f" 현재 등록된 단어 수: {len(word_list)}개")
        print("----------------------------")
        print("1. 단어 및 뜻 등록")
        print("2. 퀴즈 시작")
        print("3. 프로그램 종료")
        print("============================")
        
        choice = input("원하는 메뉴 번호를 선택하세요: ").strip()
        
        if choice == "1":
            add_word(db_file)
        elif choice == "2":
            run_quiz(db_file)
        elif choice == "3":
            print("프로그램을 종료합니다.")
            break
        else:
            print("1~3번 사이의 숫자를 입력해주세요.")

# Click CLI 설정

@click.group()
def cli():
    """영단어 마스터 CLI 프로그램"""
    pass

@cli.command()
@click.option('--name', required=True, help="사용자 이름")
def start(name):
    """프로그램을 시작하고 사용자 인증을 수행합니다."""
    click.echo(f"환영합니다! {name}님")
    
    users = load_users()
    
    # 신규 사용자
    if name not in users:
        click.echo("등록되지 않은 사용자입니다. 새로운 계정 및 단어장을 생성합니다.")
        
        password = click.prompt("사용할 비밀번호를 설정하세요", hide_input=True, confirmation_prompt=True)
        
        #파일 경로
        user_db_file = os.path.join(BASE_DIR, f"{name}_words.json")
        
        # users DB에 저장
        users[name] = {
            "password": password,
            "db_file": user_db_file
        }
        save_users(users)
        
        # 빈 단어장 파일 생성
        save_data(user_db_file, [])
        
        click.echo(f"[{name}]님의 단어장이 성공적으로 생성되었습니다!")
        interactive_menu(name, user_db_file)
        
    # 기존 고객
    else:
        while True:
            password = click.prompt("비밀번호를 입력하세요", hide_input=True)
            
            if password == users[name]["password"]:
                click.echo("비밀번호가 확인되었습니다.\n")
                interactive_menu(name, users[name]["db_file"])
                break
            else:
                click.echo("비밀번호가 틀렸습니다. 다시 입력해주세요.\n")

if __name__ == "__main__":
    cli()
