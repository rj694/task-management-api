document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const tasksContainer = document.getElementById('tasks-container');
    const newTaskBtn = document.getElementById('new-task-btn');
    const taskModal = document.getElementById('task-modal');
    const modalTitle = document.getElementById('modal-title');
    const taskForm = document.getElementById('task-form');
    const taskIdInput = document.getElementById('task-id');
    const taskTitleInput = document.getElementById('task-title');
    const taskDescriptionInput = document.getElementById('task-description');
    const taskStatusSelect = document.getElementById('task-status');
    const taskPrioritySelect = document.getElementById('task-priority');
    const taskDueDateInput = document.getElementById('task-due-date');
    const taskTagsContainer = document.getElementById('task-tags');
    const cancelTaskBtn = document.getElementById('cancel-task-btn');
    const statusFilter = document.getElementById('status-filter');
    const priorityFilter = document.getElementById('priority-filter');
    const tagFilter = document.getElementById('tag-filter');
    const searchInput = document.getElementById('search-input');
    const applyFiltersBtn = document.getElementById('apply-filters-btn');
    const prevPageBtn = document.getElementById('prev-page-btn');
    const nextPageBtn = document.getElementById('next-page-btn');
    const paginationInfo = document.getElementById('pagination-info');
    
    // State
    let currentPage = 1;
    let totalPages = 1;
    let filters = {
        status: '',
        priority: '',
        tag: '',
        search: '',
        page: 1,
        per_page: 10
    };
    
    // Initialise
    function init() {
        loadTasks();
        loadStatistics();
        setupEventListeners();
    }
    
    // Load tasks
    async function loadTasks() {
        try {
            tasksContainer.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading tasks...</div>';
            
            const data = await api.tasks.getAll({
                ...filters,
                page: currentPage
            });
            
            // Update pagination
            totalPages = data.pages;
            updatePagination();
            
            if (data.tasks.length === 0) {
                renderEmptyState();
                return;
            }
            
            tasksContainer.innerHTML = '';
            data.tasks.forEach(task => {
                tasksContainer.appendChild(createTaskCard(task));
            });
        } catch (error) {
            console.error('Error loading tasks:', error);
            tasksContainer.innerHTML = `<div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Unable to load tasks</h3>
                <p>${feedback.getUserFriendlyError(error, 'loading tasks')}</p>
                <button class="btn btn-primary" onclick="location.reload()">Try Again</button>
            </div>`;
        }
    }
    
    // Render empty state
    function renderEmptyState() {
        tasksContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-tasks"></i>
                <h3>No tasks found</h3>
                <p>${filters.search ? 'Try adjusting your search criteria' : 'Create your first task to get started'}</p>
                ${!filters.search ? '<button class="btn btn-primary" onclick="document.getElementById(\'new-task-btn\').click()">Create Task</button>' : ''}
            </div>
        `;
    }
    
    // Load task statistics
    async function loadStatistics() {
        try {
            const statistics = await api.tasks.getStatistics();
            const statisticsContent = document.getElementById('statistics-content');
            
            if (statisticsContent) {
                let html = `
                    <div class="statistics-item">
                        <span>Total Tasks:</span>
                        <span>${statistics.total_tasks}</span>
                    </div>
                `;
                
                // Status statistics
                html += '<div class="statistics-item"><span>By Status:</span></div>';
                for (const [status, count] of Object.entries(statistics.by_status)) {
                    html += `
                        <div class="statistics-item">
                            <span style="padding-left: 1rem">${status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}:</span>
                            <span>${count}</span>
                        </div>
                    `;
                }
                
                // Priority statistics
                html += '<div class="statistics-item"><span>By Priority:</span></div>';
                for (const [priority, count] of Object.entries(statistics.by_priority)) {
                    html += `
                        <div class="statistics-item">
                            <span style="padding-left: 1rem">${priority.charAt(0).toUpperCase() + priority.slice(1)}:</span>
                            <span>${count}</span>
                        </div>
                    `;
                }
                
                // Overdue and upcoming tasks
                if (statistics.overdue_tasks > 0) {
                    html += `
                        <div class="statistics-item" style="color: var(--danger-color)">
                            <span>Overdue:</span>
                            <span>${statistics.overdue_tasks}</span>
                        </div>
                    `;
                }
                
                if (statistics.upcoming_tasks > 0) {
                    html += `
                        <div class="statistics-item" style="color: var(--warning-color)">
                            <span>Due Soon:</span>
                            <span>${statistics.upcoming_tasks}</span>
                        </div>
                    `;
                }
                
                statisticsContent.innerHTML = html;
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
            const statisticsContent = document.getElementById('statistics-content');
            if (statisticsContent) {
                statisticsContent.innerHTML = '<p style="color: #999; text-align: center;">Unable to load statistics</p>';
            }
        }
    }
    
    // Create task card
    function createTaskCard(task) {
        const card = document.createElement('div');
        card.className = 'task-card';
        card.dataset.id = task.id;
        
        // Format the date
        const dueDateFormatted = task.due_date ? new Date(task.due_date).toLocaleString() : 'No due date';
        
        // Check if overdue
        const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed';
        
        // Create the tags HTML
        let tagsHTML = '';
        if (task.tags && task.tags.length > 0) {
            tagsHTML = '<div class="task-tags">';
            task.tags.forEach(tag => {
                tagsHTML += `<span class="tag" style="background-color: ${tag.color}; color: white;">${tag.name}</span>`;
            });
            tagsHTML += '</div>';
        }
        
        card.innerHTML = `
            <div class="task-header">
                <h3 class="task-title">${task.title}</h3>
                <span class="task-status ${task.status}">${task.status.replace('_', ' ')}</span>
            </div>
            <div class="task-body">
                <p class="task-description">${task.description || 'No description'}</p>
                <div class="task-meta">
                    <div>
                        <span class="task-priority ${task.priority}">
                            <i class="fas fa-flag"></i> ${task.priority}
                        </span>
                        <span class="task-due-date ${isOverdue ? 'overdue' : ''}">
                            <i class="far fa-calendar-alt"></i> ${dueDateFormatted}
                            ${isOverdue ? '<i class="fas fa-exclamation-triangle" style="color: var(--danger-color);"></i>' : ''}
                        </span>
                    </div>
                </div>
                ${tagsHTML}
            </div>
            <div class="task-footer">
                <div class="task-actions">
                    <button class="btn btn-small edit-task-btn" data-id="${task.id}">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-small btn-danger delete-task-btn" data-id="${task.id}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
                <div class="task-comments" data-id="${task.id}">
                    <i class="far fa-comment"></i> Comments
                </div>
            </div>
        `;
        
        return card;
    }
    
    // Validate task form
    function validateTaskForm() {
        let isValid = true;
        
        // Clear previous errors
        feedback.clearFieldError('task-title');
        feedback.clearFieldError('task-due-date');
        
        // Validate title
        const title = taskTitleInput.value.trim();
        if (!title) {
            feedback.showFieldError('task-title', 'Please enter a task title');
            isValid = false;
        } else if (title.length > 100) {
            feedback.showFieldError('task-title', 'Title must be less than 100 characters');
            isValid = false;
        }
        
        // Validate due date
        const dueDate = taskDueDateInput.value;
        if (dueDate) {
            const selectedDate = new Date(dueDate);
            const now = new Date();
            if (selectedDate < now && !taskIdInput.value) { // Only validate for new tasks
                feedback.showFieldError('task-due-date', 'Due date cannot be in the past');
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    // Setup task modal for creating/editing
    function setupTaskModal(mode, taskId = null) {
        // Clear previous form data
        taskForm.reset();
        taskIdInput.value = '';
        
        // Clear any validation errors
        feedback.clearFieldError('task-title');
        feedback.clearFieldError('task-due-date');
        
        // Update modal title based on mode
        modalTitle.textContent = mode === 'create' ? 'New Task' : 'Edit Task';
        
        // Load task data if editing
        if (mode === 'edit' && taskId) {
            loadTaskForEditing(taskId);
        }
        
        // Load tags for selection
        loadTagsForTaskForm();
        
        // Show modal
        taskModal.style.display = 'block';
    }
    
    // Load task data for editing
    async function loadTaskForEditing(taskId) {
        try {
            const task = await api.tasks.getById(taskId);
            
            // Populate form fields
            taskIdInput.value = task.id;
            taskTitleInput.value = task.title;
            taskDescriptionInput.value = task.description || '';
            taskStatusSelect.value = task.status;
            taskPrioritySelect.value = task.priority;
            
            // Format due date for datetime-local input
            if (task.due_date) {
                const dueDate = new Date(task.due_date);
                const localDatetime = new Date(dueDate.getTime() - dueDate.getTimezoneOffset() * 60000)
                    .toISOString()
                    .slice(0, 16);
                taskDueDateInput.value = localDatetime;
            } else {
                taskDueDateInput.value = '';
            }
            
            // Store task tags for selection after tags are loaded
            window.taskTagIds = task.tags ? task.tags.map(tag => tag.id) : [];
        } catch (error) {
            console.error('Error loading task for editing:', error);
            closeTaskModal();
            feedback.showError(error, 'loading task');
        }
    }
    
    // Load tags for task form
    async function loadTagsForTaskForm() {
        try {
            const tags = await api.tags.getAll();
            
            if (taskTagsContainer) {
                taskTagsContainer.innerHTML = '';
                
                if (tags.length === 0) {
                    taskTagsContainer.innerHTML = '<p class="help-text">No tags available. Create tags in the sidebar.</p>';
                    return;
                }
                
                tags.forEach(tag => {
                    const tagItem = document.createElement('div');
                    tagItem.className = 'task-tag-item';
                    
                    const checkbox = document.createElement('input');
                    checkbox.type = 'checkbox';
                    checkbox.id = `tag-${tag.id}`;
                    checkbox.value = tag.id;
                    checkbox.name = 'tag_ids[]';
                    
                    // Check the checkbox if tag is selected for the task
                    if (window.taskTagIds && window.taskTagIds.includes(tag.id)) {
                        checkbox.checked = true;
                    }
                    
                    const label = document.createElement('label');
                    label.htmlFor = `tag-${tag.id}`;
                    label.innerHTML = `<span class="tag" style="background-color: ${tag.color}; color: white;">${tag.name}</span>`;
                    
                    tagItem.appendChild(checkbox);
                    tagItem.appendChild(label);
                    taskTagsContainer.appendChild(tagItem);
                });
            }
        } catch (error) {
            console.error('Error loading tags for task form:', error);
            taskTagsContainer.innerHTML = '<p class="help-text" style="color: var(--danger-color);">Error loading tags. Please try again.</p>';
        }
    }
    
    // Close task modal
    function closeTaskModal() {
        taskModal.style.display = 'none';
        taskForm.reset();
        delete window.taskTagIds;
        // Clear any validation errors
        feedback.clearFieldError('task-title');
        feedback.clearFieldError('task-due-date');
    }
    
    // Update pagination buttons and info
    function updatePagination() {
        prevPageBtn.disabled = currentPage <= 1;
        nextPageBtn.disabled = currentPage >= totalPages;
        paginationInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    }
    
    // Setup event listeners
    function setupEventListeners() {
        // New task button
        if (newTaskBtn) {
            newTaskBtn.addEventListener('click', () => setupTaskModal('create'));
        }
        
        // Close modal buttons
        document.querySelectorAll('.close, #cancel-task-btn').forEach(btn => {
            btn.addEventListener('click', closeTaskModal);
        });
        
        // Task form submission
        if (taskForm) {
            taskForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                // Validate form
                if (!validateTaskForm()) {
                    return;
                }
                
                // Show loading state
                const stopLoading = feedback.showLoading(
                    document.getElementById('save-task-btn'),
                    taskIdInput.value ? 'Updating...' : 'Creating...'
                );
                
                try {
                    // Get form data
                    const formData = {
                        title: taskTitleInput.value,
                        description: taskDescriptionInput.value,
                        status: taskStatusSelect.value,
                        priority: taskPrioritySelect.value,
                        due_date: taskDueDateInput.value || null
                    };
                    
                    // Get selected tags
                    const tagCheckboxes = taskForm.querySelectorAll('input[name="tag_ids[]"]:checked');
                    if (tagCheckboxes.length > 0) {
                        formData.tag_ids = Array.from(tagCheckboxes).map(cb => parseInt(cb.value));
                    }
                    
                    // Create or update task
                    const taskId = taskIdInput.value;
                    if (taskId) {
                        await api.tasks.update(taskId, formData);
                        feedback.showSuccess('Task updated successfully!');
                    } else {
                        await api.tasks.create(formData);
                        feedback.showSuccess('Task created successfully!');
                    }
                    
                    // Close modal and reload tasks
                    closeTaskModal();
                    loadTasks();
                    loadStatistics();
                } catch (error) {
                    console.error('Error saving task:', error);
                    feedback.showError(error, 'saving the task');
                } finally {
                    stopLoading();
                }
            });
        }
        
        // Task card buttons (using event delegation)
        if (tasksContainer) {
            tasksContainer.addEventListener('click', async (e) => {
                // Edit button
                if (e.target.closest('.edit-task-btn')) {
                    const taskId = e.target.closest('.edit-task-btn').dataset.id;
                    setupTaskModal('edit', taskId);
                }
                
                // Delete button
                if (e.target.closest('.delete-task-btn')) {
                    const taskId = e.target.closest('.delete-task-btn').dataset.id;
                    const taskCard = e.target.closest('.task-card');
                    const taskTitle = taskCard.querySelector('.task-title').textContent;
                    
                    feedback.confirm(
                        `Are you sure you want to delete "${taskTitle}"? This action cannot be undone.`,
                        async () => {
                            const deleteBtn = e.target.closest('.delete-task-btn');
                            const originalContent = deleteBtn.innerHTML;
                            deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                            deleteBtn.disabled = true;
                            
                            try {
                                await api.tasks.delete(taskId);
                                feedback.showSuccess('Task deleted successfully');
                                loadTasks();
                                loadStatistics();
                            } catch (error) {
                                console.error('Error deleting task:', error);
                                feedback.showError(error, 'deleting the task');
                                // Re-enable button on error
                                deleteBtn.innerHTML = originalContent;
                                deleteBtn.disabled = false;
                            }
                        }
                    );
                }
                
                // Comments button
                if (e.target.closest('.task-comments')) {
                    const taskId = e.target.closest('.task-comments').dataset.id;
                    openCommentModal(taskId);
                }
            });
        }
        
        // Filter application
        if (applyFiltersBtn) {
            applyFiltersBtn.addEventListener('click', () => {
                filters.status = statusFilter.value;
                filters.priority = priorityFilter.value;
                filters.tag = tagFilter.value;
                filters.search = searchInput.value;
                currentPage = 1;
                loadTasks();
            });
        }
        
        // Search on enter key
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    applyFiltersBtn.click();
                }
            });
        }
        
        // Pagination buttons
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    loadTasks();
                }
            });
        }
        
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => {
                if (currentPage < totalPages) {
                    currentPage++;
                    loadTasks();
                }
            });
        }
        
        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === taskModal) {
                closeTaskModal();
            }
            
            const commentModal = document.getElementById('comment-modal');
            if (commentModal && e.target === commentModal) {
                commentModal.style.display = 'none';
            }
        });
    }
    
    // Initialise the tasks module
    init();
});