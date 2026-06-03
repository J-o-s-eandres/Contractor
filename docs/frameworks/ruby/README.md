# Ruby — OpenAPI Export Guides

## Rails (with rswag)

rswag uses an RSpec-driven approach: write request specs that double as OpenAPI definitions.

```ruby
# Gemfile
gem 'rswag-api'
gem 'rswag-ui'
gem 'rswag-specs', group: :test
```

```bash
rails generate rswag:api:install
rails generate rswag:spec:install
```

Write a spec:

```ruby
# spec/requests/api/users_spec.rb
require 'swagger_helper'

describe 'Users API' do
  path '/users/{id}' do
    get 'Retrieves a user' do
      tags 'Users'
      produces 'application/json'
      parameter name: :id, in: :path, type: :integer

      response '200', 'user found' do
        schema type: :object, properties: { id: { type: :integer }, name: { type: :string } }
        run_test!
      end
    end
  end
end
```

**Export:**
```bash
RAILS_ENV=test bundle exec rails rswag:specs:swaggerize
# Output: swagger/v1/swagger.json
```

**CI/CD:**
```yaml
- run: RAILS_ENV=test bundle exec rails rswag:specs:swaggerize
- run: contractor diff --base swagger/v1/swagger.json --candidate openapi-prod.json
```

---

## Sinatra (with swagger-blocks)

```ruby
# Gemfile
gem 'swagger-blocks'
```

```ruby
# app.rb
require 'swagger/blocks'

class MyApp < Sinatra::Base
  include Swagger::Blocks

  swagger_root do
    key :openapi, '3.0.0'
    info do
      key :version, '1.0.0'
      key :title, 'My API'
    end
  end

  swagger_schema :User do
    property :id, type: :integer
    property :name, type: :string
  end
end

# Export
spec = MyApp.swagger_docs
File.write('openapi.json', JSON.pretty_generate(spec))
```

**CI/CD:**
```yaml
- run: ruby scripts/export_openapi.rb
- run: contractor diff --base openapi-prod.json --candidate openapi.json
```
