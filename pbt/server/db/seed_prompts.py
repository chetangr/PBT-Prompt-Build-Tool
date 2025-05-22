import os
from supabase import create_client
from datetime import datetime, timedelta
import random

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def seed():
    print("🌱 Seeding database with sample data...")
    
    # Create demo user profile if not exists
    demo_user_id = "demo-user-12345"  # In real app, this would be from auth.users
    
    # Sample prompt packs with rich metadata
    prompt_packs = [
        {
            "name": "tweet_summarizer",
            "version": "0.1.0",
            "description": "Summarizes sarcastic tweets into clear meaning with context preservation.",
            "yaml_content": """name: tweet_summarizer
version: 0.1.0
description: Summarize sarcastic tweets
variables:
  - tweet
  - context
template: |
  Summarize this tweet while preserving the actual meaning behind any sarcasm:
  
  Tweet: "{{ tweet }}"
  Context: {{ context }}
  
  Provide:
  1. Literal meaning
  2. Actual intended meaning
  3. Tone analysis
examples:
  - input: {tweet: "Great, another meeting about meetings", context: "workplace"}
    output: "Literal: Expressing enthusiasm about a recursive meeting. Actual: Frustration with inefficient meeting culture. Tone: Sarcastic, exasperated."""",
            "category": "content",
            "tags": ["social-media", "nlp", "sarcasm", "summarization"],
            "user_id": demo_user_id,
            "price": 0.00,
            "is_public": True,
            "is_featured": True,
            "downloads": 245,
            "stars": 18
        },
        {
            "name": "travel_caption_gen",
            "version": "0.2.3",
            "description": "Creates poetic Instagram captions from travel photos with location awareness.",
            "yaml_content": """name: travel_caption_gen
version: 0.2.3
description: Generate travel captions
variables:
  - scene_description
  - location
  - mood
template: |
  Create an engaging Instagram caption for this travel moment:
  
  Scene: {{ scene_description }}
  Location: {{ location }}
  Desired mood: {{ mood }}
  
  Generate a caption that:
  - Captures the essence of the moment
  - Includes relevant hashtags
  - Tells a micro-story
  - Matches the desired mood
examples:
  - input: {scene_description: "Sunset over mountain lake", location: "Swiss Alps", mood: "contemplative"}
    output: "Sometimes the world stops just to show you something beautiful. Watching the day surrender to the mountains, I'm reminded that the best journeys aren't just to places, but to moments like this. 🏔️✨ #SwissAlps #MountainLife #SunsetVibes #TravelMoments #AlpineMagic"""",
            "category": "creative",
            "tags": ["travel", "social-media", "creative-writing", "instagram"],
            "user_id": demo_user_id,
            "price": 4.99,
            "is_public": True,
            "is_featured": False,
            "downloads": 127,
            "stars": 31
        },
        {
            "name": "product_reviewer_bot",
            "version": "1.0.1",
            "description": "Simulates comprehensive product review feedback based on detailed specifications.",
            "yaml_content": """name: product_reviewer_bot
version: 1.0.1
description: Generate product reviews
variables:
  - product_name
  - product_specs
  - price_range
  - target_audience
template: |
  Write a detailed product review for:
  
  Product: {{ product_name }}
  Specifications: {{ product_specs }}
  Price Range: {{ price_range }}
  Target Audience: {{ target_audience }}
  
  Include:
  - Overall rating (1-5 stars)
  - Pros and cons
  - Value for money assessment
  - Comparison with competitors
  - Recommendation for target audience
  
  Write in an authentic, helpful reviewer voice.
examples:
  - input: {product_name: "Wireless Bluetooth Headphones", product_specs: "40mm drivers, 20hr battery, ANC", price_range: "$150-200", target_audience: "commuters"}
    output: "⭐⭐⭐⭐ (4/5) These headphones excel where commuters need them most. The 20-hour battery easily handles a full work week, and the ANC effectively silences subway rumble..."""",
            "category": "analysis",
            "tags": ["product-review", "ecommerce", "analysis", "recommendation"],
            "user_id": demo_user_id,
            "price": 2.99,
            "is_public": True,
            "is_featured": True,
            "downloads": 89,
            "stars": 12
        },
        {
            "name": "code_documentor",
            "version": "1.2.0",
            "description": "Generates comprehensive documentation for code functions and classes.",
            "yaml_content": """name: code_documentor
version: 1.2.0
description: Document code automatically
variables:
  - code_snippet
  - language
  - documentation_style
template: |
  Generate documentation for this {{ language }} code:
  
  ```{{ language }}
  {{ code_snippet }}
  ```
  
  Documentation style: {{ documentation_style }}
  
  Provide:
  - Function/class description
  - Parameter descriptions with types
  - Return value description
  - Usage examples
  - Complexity notes if relevant
examples:
  - input: {code_snippet: "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)", language: "python", documentation_style: "google"}
    output: "Calculates the nth Fibonacci number using recursive approach...Args: n (int): The position in Fibonacci sequence...Returns: int: The Fibonacci number at position n..."""",
            "category": "technical",
            "tags": ["programming", "documentation", "code-analysis", "developer-tools"],
            "user_id": demo_user_id,
            "price": 7.99,
            "is_public": True,
            "is_featured": False,
            "downloads": 156,
            "stars": 24
        },
        {
            "name": "email_responder",
            "version": "0.8.5",
            "description": "Crafts professional email responses with appropriate tone and context.",
            "yaml_content": """name: email_responder
version: 0.8.5
description: Generate email responses
variables:
  - original_email
  - response_type
  - tone
  - key_points
template: |
  Craft a {{ response_type }} email response with a {{ tone }} tone:
  
  Original email:
  {{ original_email }}
  
  Key points to address:
  {{ key_points }}
  
  Generate a response that:
  - Acknowledges the original message appropriately
  - Addresses all key points clearly
  - Maintains the requested tone
  - Includes appropriate next steps
  - Follows business email etiquette
examples:
  - input: {original_email: "Hi, I'm interested in your product demo...", response_type: "sales follow-up", tone: "professional but friendly", key_points: "Schedule demo, answer pricing questions"}
    output: "Hi [Name], Thank you for your interest in our product demo! I'd be happy to walk you through our platform and answer your pricing questions. I have availability this week on..."""",
            "category": "business",
            "tags": ["email", "business-communication", "professional", "customer-service"],
            "user_id": demo_user_id,
            "price": 5.99,
            "is_public": True,
            "is_featured": False,
            "downloads": 203,
            "stars": 37
        }
    ]
    
    # Insert prompt packs
    print("📦 Inserting prompt packs...")
    for pack in prompt_packs:
        try:
            response = supabase.table("prompt_packs").insert(pack).execute()
            print(f"  ✅ {pack['name']} v{pack['version']}")
        except Exception as e:
            print(f"  ❌ Failed to insert {pack['name']}: {e}")
    
    # Generate sample evaluations
    print("📊 Generating sample evaluations...")
    
    # Get inserted prompt pack IDs
    prompt_response = supabase.table("prompt_packs").select("id, name").execute()
    prompt_ids = [(p["id"], p["name"]) for p in prompt_response.data]
    
    evaluations = []
    for pack_id, pack_name in prompt_ids:
        # Generate 3-5 evaluations per prompt
        for i in range(random.randint(3, 5)):
            eval_date = datetime.now() - timedelta(days=random.randint(1, 30))
            score = round(random.uniform(6.0, 9.5), 1)  # Bias toward good scores
            pass_rate = min(1.0, score / 10 + random.uniform(-0.1, 0.1))
            
            evaluation = {
                "prompt_id": pack_id,
                "prompt_name": pack_name,
                "score": score,
                "pass_rate": pass_rate,
                "model_used": random.choice(["claude", "gpt-4", "mistral"]),
                "test_case": {
                    "name": f"test_{i+1}",
                    "type": random.choice(["functional", "edge_case", "performance"])
                },
                "result": {
                    "passed": score >= 6.0,
                    "execution_time": random.uniform(0.5, 3.0)
                },
                "created_at": eval_date.isoformat()
            }
            evaluations.append(evaluation)
    
    # Insert evaluations in batches
    batch_size = 10
    for i in range(0, len(evaluations), batch_size):
        batch = evaluations[i:i+batch_size]
        try:
            supabase.table("evaluations").insert(batch).execute()
            print(f"  ✅ Inserted {len(batch)} evaluations")
        except Exception as e:
            print(f"  ❌ Failed to insert evaluation batch: {e}")
    
    # Generate sample analytics events
    print("📈 Generating analytics events...")
    
    events = []
    event_types = ["prompt_view", "prompt_download", "prompt_star", "evaluation_run", "prompt_edit"]
    
    for i in range(50):
        event_date = datetime.now() - timedelta(days=random.randint(1, 60))
        pack_id, pack_name = random.choice(prompt_ids)
        
        event = {
            "event_type": random.choice(event_types),
            "prompt_id": pack_id,
            "metadata": {
                "source": random.choice(["web", "api", "cli"]),
                "user_agent": "PBT/1.0"
            },
            "created_at": event_date.isoformat()
        }
        events.append(event)
    
    # Insert analytics events
    try:
        supabase.table("analytics_events").insert(events).execute()
        print(f"  ✅ Inserted {len(events)} analytics events")
    except Exception as e:
        print(f"  ❌ Failed to insert analytics events: {e}")
    
    print("\n🎉 Database seeding completed!")
    print(f"   • {len(prompt_packs)} prompt packs")
    print(f"   • {len(evaluations)} evaluations")
    print(f"   • {len(events)} analytics events")
    print("\n🌐 You can now:")
    print("   • View prompts in the gallery")
    print("   • Run evaluations")
    print("   • Check analytics dashboard")
    print("   • Test the marketplace")

if __name__ == "__main__":
    seed()
