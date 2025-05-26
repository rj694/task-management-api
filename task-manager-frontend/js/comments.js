document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const commentModal = document.getElementById('comment-modal');
    const commentTaskTitle = document.getElementById('comment-task-title');
    const commentTaskDescription = document.getElementById('comment-task-description');
    const commentsContainer = document.getElementById('comments-container');
    const commentForm = document.getElementById('comment-form');
    const commentTaskId = document.getElementById('comment-task-id');
    const commentContent = document.getElementById('comment-content');
    
    // Open comment modal
    async function openCommentModal(taskId) {
        try {
            // Get task details
            const task = await api.tasks.getById(taskId);
            
            // Set task details in modal
            commentTaskTitle.textContent = task.title;
            commentTaskDescription.textContent = task.description || 'No description';
            commentTaskId.value = task.id;
            
            // Load comments
            await loadComments(task.id);
            
            // Show modal
            commentModal.style.display = 'block';
        } catch (error) {
            console.error('Error opening comment modal:', error);
            alert(`Error loading task comments: ${error.message}`);
        }
    }
    
    // Load comments for a task
    async function loadComments(taskId) {
        try {
            commentsContainer.innerHTML = '<div class="loading">Loading comments...</div>';
            
            const comments = await api.comments.getForTask(taskId);
            
            if (comments.length === 0) {
                commentsContainer.innerHTML = '<p>No comments yet. Be the first to comment!</p>';
                return;
            }
            
            commentsContainer.innerHTML = '';
            comments.forEach(comment => {
                commentsContainer.appendChild(createCommentElement(comment));
            });
        } catch (error) {
            console.error('Error loading comments:', error);
            commentsContainer.innerHTML = `<p>Error loading comments: ${error.message}</p>`;
        }
    }
    
    // Create comment element
    function createCommentElement(comment) {
        const commentEl = document.createElement('div');
        commentEl.className = 'comment';
        commentEl.dataset.id = comment.id;
        
        // Format date
        const createdAt = new Date(comment.created_at).toLocaleString();
        
        commentEl.innerHTML = `
            <div class="comment-header">
                <span>${createdAt}</span>
                <div class="comment-actions">
                    <button class="btn btn-small edit-comment-btn" data-id="${comment.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-small btn-danger delete-comment-btn" data-id="${comment.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="comment-body">${comment.content}</div>
        `;
        
        return commentEl;
    }
    
    // Add comment
    async function addComment(taskId, content) {
        try {
            await api.comments.create(taskId, content);
            commentContent.value = '';
            await loadComments(taskId);
        } catch (error) {
            console.error('Error adding comment:', error);
            alert(`Error adding comment: ${error.message}`);
        }
    }
    
    // Edit comment
    async function editComment(commentId, content) {
        try {
            await api.comments.update(commentId, content);
            await loadComments(commentTaskId.value);
        } catch (error) {
            console.error('Error updating comment:', error);
            alert(`Error updating comment: ${error.message}`);
        }
    }
    
    // Delete comment
    async function deleteComment(commentId) {
        if (confirm('Are you sure you want to delete this comment?')) {
            try {
                await api.comments.delete(commentId);
                await loadComments(commentTaskId.value);
            } catch (error) {
                console.error('Error deleting comment:', error);
                alert(`Error deleting comment: ${error.message}`);
            }
        }
    }
    
    // Setup event listeners
    function setupEventListeners() {
        // Close modal buttons
        document.querySelectorAll('#comment-modal .close').forEach(btn => {
            btn.addEventListener('click', () => {
                commentModal.style.display = 'none';
            });
        });
        
        // Comment form submission
        if (commentForm) {
            commentForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const taskId = commentTaskId.value;
                const content = commentContent.value.trim();
                
                if (!content) {
                    alert('Please enter a comment');
                    return;
                }
                
                await addComment(taskId, content);
            });
        }
        
        // Comment actions (using event delegation)
        if (commentsContainer) {
            commentsContainer.addEventListener('click', async (e) => {
                // Edit comment button
                if (e.target.closest('.edit-comment-btn')) {
                    const commentId = e.target.closest('.edit-comment-btn').dataset.id;
                    const commentEl = e.target.closest('.comment');
                    const commentBody = commentEl.querySelector('.comment-body');
                    const currentContent = commentBody.textContent;
                    
                    const newContent = prompt('Edit your comment:', currentContent);
                    if (newContent && newContent.trim() !== currentContent) {
                        await editComment(commentId, newContent.trim());
                    }
                }
                
                // Delete comment button
                if (e.target.closest('.delete-comment-btn')) {
                    const commentId = e.target.closest('.delete-comment-btn').dataset.id;
                    await deleteComment(commentId);
                }
            });
        }
    }
    
    // Initialize
    function init() {
        setupEventListeners();
    }
    
    // Initialize the comments module
    init();
    
    // Export functions for use in other modules
    window.commentModule = {
        openCommentModal
    };
    
    // Make the openCommentModal function globally available
    window.openCommentModal = openCommentModal;
});