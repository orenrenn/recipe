with open('index.html', 'r') as f:
    text = f.read()

hallucinated = '''      const allTags = new Set();
      recipesCache.forEach(r => {
        if (r.tags && Array.isArray(r.tags)) {
          r.tags.forEach(t => allTags.add(t));
        }
      });
      Array.from(allTags).sort().forEach(tag => {
        const safeTag = escapeHtml(tag);
        if (filterTagSelect) filterTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
        if (suggestTagSelect) suggestTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
      });'''

if hallucinated in text:
    text = text.replace(hallucinated + '\n', '')
    print('Removed hallucinated block')

target = '''      Array.from(allTags).sort().forEach(tag => {
        const safeTag = escapeHtml(tag);
        if (filterTagSelect) filterTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
      });'''

replacement = '''      Array.from(allTags).sort().forEach(tag => {
        const safeTag = escapeHtml(tag);
        if (filterTagSelect) filterTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
        if (suggestTagSelect) suggestTagSelect.insertAdjacentHTML('beforeend', `<option value="${safeTag}">${safeTag}</option>`);
      });'''

if target in text:
    text = text.replace(target, replacement)
    print('Replaced target correctly')
else:
    print('Target not found')

with open('index.html', 'w') as f:
    f.write(text)
