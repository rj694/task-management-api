import click
from flask.cli import with_appcontext
from app import db
from app.utils.db_init import init_db, drop_db, create_sample_data
from app.models.user import User
from app.utils.cleanup import cleanup_expired_tokens

def register_commands(app):
    """Register custom Flask CLI commands."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(drop_db_command)
    app.cli.add_command(create_sample_data_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(cleanup_tokens_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database."""
    init_db()

@click.command('drop-db')
@with_appcontext
def drop_db_command():
    """Drop all database tables."""
    if click.confirm('Are you sure you want to drop all tables?'):
        drop_db()
    else:
        click.echo('Operation cancelled.')

@click.command('create-sample-data')
@with_appcontext
def create_sample_data_command():
    """Create sample data for development."""
    if click.confirm('Are you sure you want to create sample data?'):
        create_sample_data()
    else:
        click.echo('Operation cancelled.')

@click.command('create-admin')
@click.option('--username', prompt=True, help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
@with_appcontext
def create_admin_command(username, email, password):
    """Create an admin user."""
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        click.echo(f"User with email {email} already exists.")
        return
    
    if User.query.filter_by(username=username).first():
        click.echo(f"User with username {username} already exists.")
        return
    
    # Create admin user
    user = User(
        username=username,
        email=email,
        password=password,
        role='admin'
    )
    
    # Add user to database
    db.session.add(user)
    db.session.commit()
    
    click.echo(f"Admin user {username} created successfully.")

@click.command('cleanup-tokens')
@with_appcontext
def cleanup_tokens_command():
    """Clean up expired tokens from the blacklist."""
    result = cleanup_expired_tokens()
    
    if result >= 0:
        click.echo(f"Removed {result} expired tokens from the blacklist.")
    else:
        click.echo("Error cleaning up expired tokens.")