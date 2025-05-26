from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models.user import User
from app.models.task import Task
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

# Create shell context
@app.shell_context_processor
def make_shell_context():
    """Create shell context for Flask CLI."""
    return {
        'db': db,
        'User': User,
        'Task': Task
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)