import os
secret_key = os.urandom(12).hex()
print(secret_key)
# 3790e43fe46c103ebf40b526 
# stick to one key throughout development