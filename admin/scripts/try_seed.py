from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import os
print('FLASK_ENV before:', os.getenv('FLASK_ENV'))

from admin import create_app
app = create_app()
with app.app_context():
    print('FLASK_ENV in app context:', os.getenv('FLASK_ENV'))
    from admin.db.seed import seed_development_data
    from admin import models
    print('seed_development_data:', seed_development_data)
    try:
        seed_development_data(models.db, app)
        print('seed completed')
    except Exception as e:
        import traceback
        print('seed exception:')
        traceback.print_exc()
