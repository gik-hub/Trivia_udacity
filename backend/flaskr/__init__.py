from crypt import methods
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
from models import Category

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)
    
    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    #   CORS(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    
    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers 
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response
    
    # Route specific CORS access
    @app.route('/messages')
    @cross_origin()
    def get_messages():
        return 'GETTING MESSAGES'


    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        all_categories = Category.query.all()
        # categories dict for holding the retrives categories
        categoriesDict = {}

        # adding all categories to the dict
        for category in all_categories:
            categoriesDict[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': categoriesDict
        })

    @app.route('/categories/<int:catgory_id>', methods=['GET', 'PATCH'])
    def category(catgory_id):
        category = Category.query.filter(Category.id == catgory_id).one_or_none()
        
        if category is None:
            abort(404)
        else:
            return jsonify({'success': True,
                        'data': category.format(),
                        })

        
    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    
    @app.route('/questions')
    def get_questions():
        try:
            all_questions = Question.query.order_by(Question.id).all()
            paqinated_qns = paginate_questions(request, all_questions)

            if (len(paqinated_qns) == 0):
                abort(404)

            categories = Category.query.all()
            categoriesDict = {}
            for category in categories:
                categoriesDict[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': paqinated_qns,
                'total_questions': len(all_questions),
                'categories': categoriesDict
            })
        except Exception as e:
            print(e)
            abort(400)
        
        

    """ 
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
            
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter_by(id=question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            all_questions = Question.query.order_by(Question.id).all()
            currentQuestions = paginate_questions(request, all_questions)

            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(all_questions)
            })

        except Exception as e:
            print(e)
            abort(404)
    

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        dificulty = body.get("dificulty", None)
        
        try:
            # add ..
            question = Question(question=question, answer=answer,
                                category=category, difficulty=dificulty)
            question.insert()

            current_questions = Question.query.order_by(Question.id).all()
            formatted_questions = [current_questions.format() for question in current_questions]

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': formatted_questions,
                'total_questions': len(current_questions)
            })

        except Exception as e:
            print(e)
            abort(422)
        

    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    
    @app.route("/search", methods=['POST'])
    def search():
        body = request.get_json()
        search = body.get('searchTerm')
        all_questions = Question.query.filter(
            Question.question.ilike('%'+search+'%')).all()

        if all_questions:
            current_questions = paginate_questions(request, all_questions)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(all_questions)
            })
        else:
            abort(404)


    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions")
    def questions_in_category(id):
        category = Category.query.filter_by(id=id).one_or_none()
        if category:
            category_questions = Question.query.filter_by(category=str(id)).all()
            current_questions = paginate_questions(request, category_questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(category_questions),
                'current_category': category.type
            })
        else:
            abort(404)

    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        # get the qestion category an the previous question
        body = request.get_json()
        quizCategory = body.get('quiz_category')
        previousQuestion = body.get('previous_questions')

        try:
            if (quizCategory['id'] == 0):
                questionsQuery = Question.query.all()
            else:
                questionsQuery = Question.query.filter_by(
                    category=quizCategory['id']).all()

            randomIndex = random.randint(0, len(questionsQuery)-1)
            nextQuestion = questionsQuery[randomIndex]

            stillQuestions = True
            while nextQuestion.id not in previousQuestion:
                nextQuestion = questionsQuery[randomIndex]
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": nextQuestion.answer,
                        "category": nextQuestion.category,
                        "difficulty": nextQuestion.difficulty,
                        "id": nextQuestion.id,
                        "question": nextQuestion.question
                    },
                    'previousQuestion': previousQuestion
                })

        except Exception as e:
            print(e)
            abort(404)

    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400 
        
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not found"
            }), 404
        
    @app.errorhandler(422)
    def unprocessable_recource(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable recource"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500
        
    return app

