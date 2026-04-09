import boto3

def list_profiles():
    client = boto3.client("bedrock", region_name="ap-northeast-1")
    try:
        response = client.list_inference_profiles()
        print("--- 東京リージョンで利用可能な推論プロファイル ---")
        found = False
        for profile in response.get("inferenceProfileSummaries", []):
            if "nova-micro" in profile.get("inferenceProfileId", ""):
                print(f"ID  : {profile.get('inferenceProfileId')}")
                print(f"Name: {profile.get('inferenceProfileName')}")
                print(f"ARN : {profile.get('inferenceProfileArn')}")
                print("-" * 30)
                found = True
        
        if not found:
            print("Nova Micro 用の推論プロファイルが見つかりませんでした。")
            print("すべてのプロファイルを表示します:")
            for profile in response.get("inferenceProfileSummaries", []):
                print(f"- {profile.get('inferenceProfileId')}")
                
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    list_profiles()
