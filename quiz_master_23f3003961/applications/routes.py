from datetime import datetime
from flask import app, flash, render_template, request, redirect, session, url_for
from applications.model import db, User, Subject, Chapter, Quiz, Question, Score  # Import required models

def init_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()

            if user and user.password == password:  # Check if user exists & password matches
                session['user_id'] = user.id  
                session['username'] = user.username

                if username == 'admin@abc.com':  # Redirect admin to dashboard
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))  # Redirect users to dashboard

            else:
                flash("Invalid username or password", "danger")

        return render_template('login.html')


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            fullname = request.form['fullname']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            new_user = User(fullname=fullname, username=username, email=email, password=password)

            db.session.add(new_user)  
            db.session.commit()  

            return redirect(url_for('login'))  

        return render_template('register.html')

    @app.route('/admin_dashboard')
    def admin_dashboard():
        if 'username' not in session or session['username'] != 'admin@abc.com':
            flash("Unauthorized access!", "danger")
            return redirect(url_for('login'))  # Redirect unauthorized users

        subjects = Subject.query.all()  
        chapters = Chapter.query.all()  
        quizzes = Quiz.query.all()  
        users = User.query.all()
        questions =  Question.query.all()

        total_users = len(users)
        total_subjects = len(subjects)
        total_chapters = len(chapters)
        total_quizzes = len(quizzes)
        total_questions = len(questions)

        return render_template(
            'admin_dashboard.html', 
            subjects=subjects, 
            chapters=chapters, 
            quizzes=quizzes, 
            users=users,
            questions=questions,
            total_users=total_users,
            total_subjects=total_subjects,
            total_chapters=total_chapters,
            total_quizzes=total_quizzes,
            total_questions=total_questions)
        
    ########
        
    @app.route('/manage_users', methods=['GET', 'POST'])
    def manage_users():
        if request.method == 'POST':
            user_id = request.args.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                if user:
                    db.session.delete(user)
                    db.session.commit()
                    flash('User deleted successfully!', 'success')
                else:
                    flash('User not found!', 'error')
            return redirect(url_for('manage_users'))

        # Handling search functionality
        search_query = request.args.get('search', '').strip()
        if search_query:
            users = User.query.filter(User.username.ilike(f"%{search_query}%")).all()
        else:
            users = User.query.all()

        return render_template('manage_users.html', users=users)

    @app.route('/delete_user/<int:user_id>', methods=['POST'])
    def delete_user(user_id):
        user = User.query.get(user_id)
        if user:
            # Delete all scores related to the user first
            Score.query.filter_by(user_id=user.id).delete()
            
            db.session.delete(user)
            db.session.commit()
            flash(f"User {user.username} has been deleted successfully.", "success")
        else:
            flash("User not found.", "danger")

        return redirect(url_for('manage_users'))

    #########
    
    @app.route('/manage_subjects', methods=['GET', 'POST'])
    def manage_subjects():
        if request.method == 'POST':
            subject_name = request.form.get('subject_name')
            subject_desc = request.form.get('subject_desc')

            # Check if subject already exists
            existing_subject = Subject.query.filter_by(name=subject_name).first()
            if existing_subject:
                flash("Subject already exists!", "danger")
            else:
                new_subject = Subject(name=subject_name, description=subject_desc)
                db.session.add(new_subject)
                db.session.commit()
                flash("Subject added successfully!", "success")

            return redirect(url_for('manage_subjects'))

        # Handle search functionality
        search_query = request.args.get('search', '').strip()
        if search_query:
            subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()
        else:
            subjects = Subject.query.all()

        return render_template('manage_subjects.html', subjects=subjects)
    
    @app.route('/delete_subject/<int:subject_id>', methods=['POST'])
    def delete_subject(subject_id):
        subject = Subject.query.get(subject_id)
        if subject:
            db.session.delete(subject)
            db.session.commit()
            flash("Subject deleted!", "success")
        return redirect(url_for('manage_subjects'))
    
    @app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
    def edit_subject(subject_id):
        subject = Subject.query.get(subject_id)

        if request.method == 'POST':
            subject.name = request.form.get('subject_name')
            subject.description = request.form.get('subject_desc')
            db.session.commit()
            flash("Subject updated successfully!", "success")
            return redirect(url_for('manage_subjects'))

        return render_template('edit_subject.html', subject=subject)

    #########
    
    @app.route('/manage_chapters', methods=['GET', 'POST'])
    def manage_chapters():
        subjects = Subject.query.all()  # Fetch all subjects for the dropdown

        # Handle search functionality
        search_query = request.args.get('search', '')
        if search_query:
            chapters = Chapter.query.filter(Chapter.name.ilike(f'%{search_query}%')).all()
        else:
            chapters = Chapter.query.all()

        if request.method == 'POST':
            chapter_name = request.form.get('chapter_name')
            subject_id = request.form.get('subject_id')

            if not chapter_name or not subject_id:
                flash("Please fill all fields", "danger")
            else:
                new_chapter = Chapter(name=chapter_name, subject_id=subject_id)
                db.session.add(new_chapter)
                db.session.commit()
                flash("Chapter added successfully!", "success")
                return redirect(url_for('manage_chapters'))

        return render_template('manage_chapters.html', subjects=subjects, chapters=chapters)

    
    @app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
    def edit_chapter(chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        subjects = Subject.query.all()  # Fetch all subjects for the dropdown

        if request.method == 'POST':
            chapter.name = request.form['chapter_name']
            chapter.subject_id = int(request.form['subject_id'])  # Update subject ID
            db.session.commit()
            flash('Chapter updated successfully!', 'success')
            return redirect(url_for('manage_chapters'))

        return render_template('edit_chapter.html', chapter=chapter, subjects=subjects)
        
    @app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
    def delete_chapter(chapter_id):
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        flash("Chapter deleted successfully!", "success")
        return redirect(url_for('manage_chapters'))
    
    #########
    
    @app.route('/manage_quizzes')
    def manage_quizzes():
        search_query = request.args.get('search', '')  
        if search_query:
            quizzes = Quiz.query.filter(Quiz.name.ilike(f"%{search_query}%")).all()
        else:
            quizzes = Quiz.query.all()
        
        chapters = Chapter.query.all()  
        return render_template('manage_quizzes.html', quizzes=quizzes, chapters=chapters, search_query=search_query)

    @app.route('/manage_quizzes', methods=['POST'])
    def add_quiz():
        name = request.form.get('name')
        chapter_id = request.form.get('chapter_id')
        date_of_quiz_str = request.form.get('date_of_quiz')  
        time_duration = request.form.get('time_duration')
        remarks = request.form.get('remarks')

        try:
            date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d")  
        except ValueError:
            flash("Invalid date format. Please enter a valid date.", "error")
            return redirect(url_for('manage_quizzes'))

        new_quiz = Quiz(
            name=name,
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )

        db.session.add(new_quiz)
        db.session.commit()
        flash("Quiz added successfully!", "success")

        return redirect(url_for('manage_quizzes'))

    @app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
    def edit_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        chapters = Chapter.query.all()  # Fetch chapters for the dropdown

        if request.method == 'POST':
            quiz.name = request.form.get('name')
            quiz.chapter_id = request.form.get('chapter_id')
            date_of_quiz_str = request.form.get('date_of_quiz')
            quiz.time_duration = request.form.get('time_duration')
            quiz.remarks = request.form.get('remarks')

            try:
                quiz.date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d")
            except ValueError:
                flash("Invalid date format. Please enter a valid date.", "error")
                return redirect(url_for('edit_quiz', quiz_id=quiz.id))

            db.session.commit()
            flash("Quiz updated successfully!", "success")
            return redirect(url_for('manage_quizzes'))

        return render_template('edit_quiz.html', quiz=quiz, chapters=chapters)

    @app.route('/delete_quiz/<int:quiz_id>')
    def delete_quiz(quiz_id):
        quiz = Quiz.query.get(quiz_id)
        if quiz:
            db.session.delete(quiz)
            db.session.commit()
            flash("Quiz deleted successfully!", "success")
        else:
            flash("Quiz not found", "error")

        return redirect(url_for('manage_quizzes'))

    #########
    
    @app.route('/manage_questions')
    def manage_questions():
        subject_id = request.args.get('subject', type=int)  # Convert to int
        chapter_id = request.args.get('chapter', type=int)  # Convert to int
        quiz_id = request.args.get('quiz', type=int)  # Convert to int

        # Get questions related to the selected quiz and order them by ID
        questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.id).all() if quiz_id else []

        # Get all subjects
        subjects = Subject.query.all()

        # Get chapters related to the selected subject
        chapters = Chapter.query.filter_by(subject_id=subject_id).all() if subject_id else []

        # Get quizzes related to the selected chapter
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all() if chapter_id else []

        return render_template(
            'manage_questions.html',
            subjects=subjects,
            chapters=chapters,
            quizzes=quizzes,
            questions=questions,
            selected_subject=subject_id,
            selected_chapter=chapter_id,
            selected_quiz=quiz_id
        )

    @app.route('/add_question', methods=['GET', 'POST'])
    def add_question():
        quiz_id = request.args.get('quiz')

        if request.method == 'POST':
            question_text = request.form.get('question_text')
            option1 = request.form.get('option1')
            option2 = request.form.get('option2')
            option3 = request.form.get('option3')
            option4 = request.form.get('option4')
            correct_option = request.form.get('correct_option')

            if quiz_id and question_text:
                new_question = Question(
                    quiz_id=quiz_id,
                    question_statement=question_text,
                    option1=option1,
                    option2=option2,
                    option3=option3,
                    option4=option4,
                    correct_option=correct_option
                )
                db.session.add(new_question)
                db.session.commit()

                return redirect(url_for('manage_questions', quiz=quiz_id))

        return render_template('add_question.html', quiz_id=quiz_id)


    @app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
    def edit_question(question_id):
        question = Question.query.get_or_404(question_id)

        if request.method == 'POST':
            question.question_statement = request.form.get('question_statement')
            question.option1 = request.form.get('option1')
            question.option2 = request.form.get('option2')
            question.option3 = request.form.get('option3')
            question.option4 = request.form.get('option4')
            question.correct_option = request.form.get('correct_option')

            try:
                db.session.commit()
                flash("Question updated successfully!", "success")
                return redirect(url_for('manage_questions'))
            except Exception as e:
                flash(f"Error updating question: {e}", "error")
                return redirect(url_for('edit_question', question_id=question.id))

        return render_template('edit_question.html', question=question)

    @app.route('/delete_question/<int:question_id>', methods=['GET'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question:
            try:
                db.session.delete(question)
                db.session.commit()
                flash("Question deleted successfully!", "success")
            except Exception as e:
                flash(f"Error deleting question: {e}", "error")
        else:
            flash("Question not found", "error")

        return redirect(url_for('manage_questions'))
    
    ######## 
    
    @app.route('/user_dashboard')
    def user_dashboard():
        if 'user_id' not in session:
            flash("Please log in first", "warning")
            return redirect(url_for('login'))

        user_id = session['user_id']

        # Fetch available quizzes
        available_quizzes = db.session.query(
            Subject.name, Chapter.name, Quiz.id, Quiz.name
        ).join(Chapter, Subject.id == Chapter.subject_id)\
        .join(Quiz, Chapter.id == Quiz.chapter_id).all()
        
        # Fetch previously attempted quizzes
        attempted_quizzes = db.session.query(
            Subject.name, Chapter.name, Quiz.name, Score.total_scored, 
            db.func.count(Question.id), Score.time_stamp_of_attempt
        ).join(Chapter, Subject.id == Chapter.subject_id)\
        .join(Quiz, Chapter.id == Quiz.chapter_id)\
        .join(Score, Quiz.id == Score.quiz_id)\
        .join(Question, Quiz.id == Question.quiz_id)\
        .filter(Score.user_id == user_id).group_by(Score.id).all()

        return render_template("user_dashboard.html", available_quizzes=available_quizzes, attempted_quizzes=attempted_quizzes)

    @app.route('/attempt_quiz/<int:quiz_id>')
    def attempt_quiz(quiz_id):
        if 'user_id' not in session:
            flash("Please log in first", "warning")
            return redirect(url_for('login'))

        return redirect(url_for('take_quiz', quiz_id=quiz_id))
    
    @app.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
    def take_quiz(quiz_id):
        if 'user_id' not in session:
            flash("Please log in to attempt a quiz.", "danger")
            return redirect(url_for('login'))

        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        if request.method == 'POST':
            user_id = session['user_id']
            total_questions = len(questions)
            correct_answers = 0

            for question in questions:
                selected_option = request.form.get(f'question_{question.id}')
                if selected_option == question.correct_option:
                    correct_answers += 1

            percentage_score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

            # Store score in the database
            new_score = Score(
                quiz_id=quiz_id,
                user_id=user_id,
                total_scored=correct_answers,
                time_stamp_of_attempt=datetime.now()
            )
            db.session.add(new_score)
            db.session.commit()

            flash(f"You scored {percentage_score:.2f}%", "success")
            return redirect(url_for('user_dashboard'))

        return render_template('take_quiz.html', quiz=quiz, questions=questions)

