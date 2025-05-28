
echo "Running Health Record API Tests..."
echo "================================="

export DJANGO_SETTINGS_MODULE=test_settings

python -m pytest \
    --cov=apps \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-branch \
    -v

echo ""
echo "Coverage report generated in htmlcov/index.html"