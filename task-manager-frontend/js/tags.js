document.addEventListener('DOMContentLoaded', () => {
    // DOM elements
    const tagsList = document.getElementById('tags-list');
    const newTagName = document.getElementById('new-tag-name');
    const newTagColor = document.getElementById('new-tag-color');
    const addTagBtn = document.getElementById('add-tag-btn');
    const tagFilter = document.getElementById('tag-filter');
    
    // Load tags
    async function loadTags() {
        try {
            const tags = await api.tags.getAll();
            
            // Update tags list
            if (tagsList) {
                tagsList.innerHTML = '';
                
                if (tags.length === 0) {
                    tagsList.innerHTML = '<p>No tags created yet.</p>';
                    return;
                }
                
                tags.forEach(tag => {
                    const tagElement = document.createElement('span');
                    tagElement.className = 'tag';
                    tagElement.dataset.id = tag.id;
                    tagElement.style.backgroundColor = tag.color;
                    tagElement.style.color = 'white';
                    tagElement.innerHTML = `
                        ${tag.name}
                        <i class="fas fa-times delete-tag" data-id="${tag.id}"></i>
                    `;
                    tagsList.appendChild(tagElement);
                });
            }
            
            // Update tag filter
            if (tagFilter) {
                // Save current selection
                const currentValue = tagFilter.value;
                
                // Clear options except first "All" option
                while (tagFilter.options.length > 1) {
                    tagFilter.options.remove(1);
                }
                
                // Add tag options
                tags.forEach(tag => {
                    const option = document.createElement('option');
                    option.value = tag.id;
                    option.textContent = tag.name;
                    tagFilter.appendChild(option);
                });
                
                // Restore selection if possible
                if (currentValue) {
                    tagFilter.value = currentValue;
                }
            }
        } catch (error) {
            console.error('Error loading tags:', error);
            if (tagsList) {
                tagsList.innerHTML = '<p>Error loading tags. Please try again.</p>';
            }
        }
    }
    
    // Create a new tag
    async function createTag() {
        const name = newTagName.value.trim();
        const color = newTagColor.value;
        
        if (!name) {
            alert('Please enter a tag name');
            return;
        }
        
        try {
            await api.tags.create({ name, color });
            newTagName.value = '';
            loadTags();
        } catch (error) {
            console.error('Error creating tag:', error);
            alert(`Error creating tag: ${error.message}`);
        }
    }
    
    // Delete a tag
    async function deleteTag(tagId) {
        if (confirm('Are you sure you want to delete this tag?')) {
            try {
                await api.tags.delete(tagId);
                loadTags();
            } catch (error) {
                console.error('Error deleting tag:', error);
                alert(`Error deleting tag: ${error.message}`);
            }
        }
    }
    
    // Setup event listeners
    function setupEventListeners() {
        // Add tag button
        if (addTagBtn) {
            addTagBtn.addEventListener('click', createTag);
        }
        
        // New tag input - submit on Enter
        if (newTagName) {
            newTagName.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    createTag();
                }
            });
        }
        
        // Delete tag buttons (using event delegation)
        if (tagsList) {
            tagsList.addEventListener('click', (e) => {
                if (e.target.classList.contains('delete-tag')) {
                    const tagId = e.target.dataset.id;
                    deleteTag(tagId);
                }
            });
        }
    }
    
    // Initialize
    function init() {
        loadTags();
        setupEventListeners();
    }
    
    // Initialize the tags module
    init();
    
    // Export functions for use in other modules
    window.tagsModule = {
        loadTags
    };
});