# Template for Converting Documentation to Collapsible Format

## Pattern 1: Simple Function Dropdowns
```rst
.. dropdown:: function_name - Short Description
   :color: primary
   :icon: relevant-icon

   .. automodule:: vivainsights.function_name
      :members:
      :undoc-members:
      :show-inheritance:
```

## Pattern 2: Grouped Category Dropdowns
```rst
.. dropdown:: 📊 Category Name (X functions)
   :color: info
   :open:

   Click to explore functions in this category:

   .. dropdown:: function1 - Description
      :color: light

      .. automodule:: vivainsights.function1
         :members:
         :undoc-members:
         :show-inheritance:

   .. dropdown:: function2 - Description  
      :color: light

      .. automodule:: vivainsights.function2
         :members:
         :undoc-members:
         :show-inheritance:
```

## Pattern 3: Quick Reference with Detailed Dropdowns
```rst
.. list-table:: Function Quick Reference
   :widths: 20 20 60
   :header-rows: 1

   * - Function
     - Purpose
     - Documentation
   * - ``create_bar()``
     - Bar charts
     - .. dropdown:: View Details
          :color: primary

          .. autofunction:: vivainsights.create_bar
```

## Benefits:
1. **Better Scanning**: Users can quickly see all available functions
2. **Progressive Disclosure**: Details only shown when needed
3. **Improved Performance**: Page loads faster with collapsed content
4. **Better Mobile Experience**: Collapsible sections work great on mobile
5. **Visual Hierarchy**: Colors and icons help categorize functions

## Recommended Colors:
- `primary` (blue): Core visualization functions
- `secondary` (gray): Utility functions  
- `success` (green): Data processing functions
- `info` (cyan): Analysis functions
- `warning` (yellow): Identification functions
- `danger` (red): Advanced/experimental functions

## Recommended Icons:
- `chart-bar`: Bar charts
- `chart-line`: Line charts  
- `chart-area`: Area/box plots
- `circle-dot`: Bubble/scatter plots
- `diagram-project`: Network/flow diagrams
- `calendar-days`: Time-based functions
- `magnifying-glass`: Analysis functions
- `gear`: Utility functions
- `database`: Data functions
