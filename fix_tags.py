with open('index.html', 'r') as f:
    text = f.read()

# First, remove the tags logic from renderGrid
to_remove = '''      const allTags = new Set();
      recipesCache.forEach(r => {
        if (r.tags && Array.isArray(r.tags)) {
          r.tags.forEach(t => allTags.add(t));
        }
      });
      Array.from(allTags).sort().forEach(tag => {
        const safeTag = escapeHtml(tag);
        if (filterTagSelect) filterTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
        if (suggestTagSelect) suggestTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
      });

'''

if to_remove in text:
    text = text.replace(to_remove, '')
    print("Removed from renderGrid")
else:
    print("Not found in renderGrid!")

# Now replace updateFilterTagsUI
old_func = '''    function updateFilterTagsUI() {
      const filterTagSelect = document.getElementById('filter-tag-select');
      const suggestTagSelect = document.getElementById('suggest-tag-select');
      const currentFilter = filterTagSelect ? filterTagSelect.value : '';
      const currentSuggestFilter = suggestTagSelect ? suggestTagSelect.value : '';

      if (filterTagSelect) {
        filterTagSelect.innerHTML = '<option value="">すべてのタグ</option>';
      }
      if (suggestTagSelect) {
        suggestTagSelect.innerHTML = '<option value="">すべてのタグ</option>';
      }

      if (filterTagSelect) filterTagSelect.value = currentFilter;
      if (suggestTagSelect) suggestTagSelect.value = currentSuggestFilter;
    }'''

new_func = '''    function updateFilterTagsUI() {
      const filterTagSelect = document.getElementById('filter-tag-select');
      const suggestTagSelect = document.getElementById('suggest-tag-select');
      const currentFilter = filterTagSelect ? filterTagSelect.value : '';
      const currentSuggestFilter = suggestTagSelect ? suggestTagSelect.value : '';

      if (filterTagSelect) {
        filterTagSelect.innerHTML = '<option value="">すべてのタグ</option>';
      }
      if (suggestTagSelect) {
        suggestTagSelect.innerHTML = '<option value="">すべてのタグ</option>';
      }

      const allTags = new Set();
      recipesCache.forEach(r => {
        if (r.tags && Array.isArray(r.tags)) {
          r.tags.forEach(t => allTags.add(t));
        }
      });
      
      Array.from(allTags).sort().forEach(tag => {
        const safeTag = escapeHtml(tag);
        if (filterTagSelect) filterTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
        if (suggestTagSelect) suggestTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
      });

      if (filterTagSelect) filterTagSelect.value = currentFilter;
      if (suggestTagSelect) suggestTagSelect.value = currentSuggestFilter;
    }'''

if old_func in text:
    text = text.replace(old_func, new_func)
    print("Replaced updateFilterTagsUI")
else:
    print("Not found old_func!")

with open('index.html', 'w') as f:
    f.write(text)

