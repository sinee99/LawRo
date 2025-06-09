#!/bin/bash

# LawRo Contract Analyzer AWS 배포 스크립트
set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 사용법 출력
usage() {
    echo "사용법: $0 [OPTIONS]"
    echo ""
    echo "옵션:"
    echo "  -r, --region REGION           AWS 리전 (기본값: ap-northeast-2)"
    echo "  -a, --account-id ACCOUNT_ID   AWS 계정 ID (필수)"
    echo "  -k, --upstage-key KEY         Upstage API Key (필수)"
    echo "  -b, --bucket-name BUCKET      S3 버킷 이름 (기본값: lawro-contracts-{RANDOM})"
    echo "  -p, --project-name NAME       프로젝트 이름 (기본값: lawro)"
    echo "  -e, --environment ENV         환경 (기본값: production)"
    echo "  --skip-infra                  인프라 생성 건너뛰기"
    echo "  --skip-build                  이미지 빌드 건너뛰기"
    echo "  --skip-deploy                 서비스 배포 건너뛰기"
    echo "  -h, --help                    도움말 출력"
    echo ""
    echo "예시:"
    echo "  $0 -a 123456789012 -k up_xxxxx -b my-lawro-bucket"
    exit 1
}

# 기본값 설정
AWS_REGION="ap-northeast-2"
PROJECT_NAME="lawro"
ENVIRONMENT="production"
SKIP_INFRA=false
SKIP_BUILD=false
SKIP_DEPLOY=false

# 파라미터 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -a|--account-id)
            AWS_ACCOUNT_ID="$2"
            shift 2
            ;;
        -k|--upstage-key)
            UPSTAGE_API_KEY="$2"
            shift 2
            ;;
        -b|--bucket-name)
            S3_BUCKET_NAME="$2"
            shift 2
            ;;
        -p|--project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-infra)
            SKIP_INFRA=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-deploy)
            SKIP_DEPLOY=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "알 수 없는 옵션: $1"
            usage
            ;;
    esac
done

# 필수 파라미터 확인
if [[ -z "$AWS_ACCOUNT_ID" ]]; then
    log_error "AWS 계정 ID가 필요합니다. -a 옵션을 사용하세요."
    usage
fi

if [[ -z "$UPSTAGE_API_KEY" ]]; then
    log_error "Upstage API Key가 필요합니다. -k 옵션을 사용하세요."
    usage
fi

# S3 버킷 이름 기본값 설정 (유니크하게)
if [[ -z "$S3_BUCKET_NAME" ]]; then
    RANDOM_SUFFIX=$(date +%s | tail -c 6)
    S3_BUCKET_NAME="${PROJECT_NAME}-contracts-${RANDOM_SUFFIX}"
fi

# AWS CLI 설치 확인
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI가 설치되지 않았습니다."
    exit 1
fi

# Docker 설치 확인
if ! command -v docker &> /dev/null; then
    log_error "Docker가 설치되지 않았습니다."
    exit 1
fi

# 스크립트 시작
log_info "🚀 LawRo Contract Analyzer AWS 배포 시작"
log_info "프로젝트: $PROJECT_NAME"
log_info "환경: $ENVIRONMENT"
log_info "리전: $AWS_REGION"
log_info "계정 ID: $AWS_ACCOUNT_ID"
log_info "S3 버킷: $S3_BUCKET_NAME"

# AWS 인증 확인
log_info "AWS 인증 확인 중..."
aws sts get-caller-identity --region $AWS_REGION > /dev/null
log_success "AWS 인증 확인 완료"

# 1. 인프라 생성 (CloudFormation)
if [[ "$SKIP_INFRA" == false ]]; then
    log_info "📦 AWS 인프라 생성 중..."
    
    STACK_NAME="${PROJECT_NAME}-infrastructure"
    
    # CloudFormation 스택 배포
    aws cloudformation deploy \
        --template-file aws/cloudformation-template.yaml \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --capabilities CAPABILITY_NAMED_IAM \
        --parameter-overrides \
            ProjectName=$PROJECT_NAME \
            Environment=$ENVIRONMENT \
            UpstageApiKey=$UPSTAGE_API_KEY \
            S3BucketName=$S3_BUCKET_NAME
    
    if [[ $? -eq 0 ]]; then
        log_success "인프라 생성 완료"
    else
        log_error "인프라 생성 실패"
        exit 1
    fi
    
    # 스택 출력값 가져오기
    log_info "스택 출력값 조회 중..."
    CHATBOT_ECR_URI=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ChatbotECRRepository`].OutputValue' \
        --output text)
    
    CONTRACT_ANALYZER_ECR_URI=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ContractAnalyzerECRRepository`].OutputValue' \
        --output text)
    
    CLUSTER_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
        --output text)
    
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    log_success "스택 출력값 조회 완료"
else
    log_warning "인프라 생성을 건너뜁니다."
    # 기존 스택에서 값 조회
    STACK_NAME="${PROJECT_NAME}-infrastructure"
    CHATBOT_ECR_URI=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ChatbotECRRepository`].OutputValue' \
        --output text)
    CONTRACT_ANALYZER_ECR_URI=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ContractAnalyzerECRRepository`].OutputValue' \
        --output text)
    CLUSTER_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ECSClusterName`].OutputValue' \
        --output text)
    ALB_DNS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
fi

# 2. Docker 이미지 빌드 및 푸시
if [[ "$SKIP_BUILD" == false ]]; then
    log_info "🔨 Docker 이미지 빌드 및 푸시 중..."
    
    # ECR 로그인
    log_info "ECR에 로그인 중..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Chatbot 이미지 빌드 및 푸시
    log_info "Chatbot 이미지 빌드 중..."
    docker build -t $CHATBOT_ECR_URI:latest ../chatbot-docker/
    docker push $CHATBOT_ECR_URI:latest
    
    # Contract Analyzer 이미지 빌드 및 푸시
    log_info "Contract Analyzer 이미지 빌드 중..."
    docker build -t $CONTRACT_ANALYZER_ECR_URI:latest .
    docker push $CONTRACT_ANALYZER_ECR_URI:latest
    
    log_success "Docker 이미지 빌드 및 푸시 완료"
else
    log_warning "이미지 빌드를 건너뜁니다."
fi

# 3. ECS 서비스 배포
if [[ "$SKIP_DEPLOY" == false ]]; then
    log_info "🚀 ECS 서비스 배포 중..."
    
    # Task Definition 업데이트
    TASK_DEF_JSON=$(cat aws/task-definition.json | \
        sed "s/{AWS_ACCOUNT_ID}/$AWS_ACCOUNT_ID/g" | \
        sed "s/{AWS_REGION}/$AWS_REGION/g" | \
        sed "s/{UPSTAGE_API_KEY}/$UPSTAGE_API_KEY/g" | \
        sed "s/{S3_BUCKET_NAME}/$S3_BUCKET_NAME/g")
    
    # Task Definition 등록
    TASK_DEF_ARN=$(echo "$TASK_DEF_JSON" | aws ecs register-task-definition \
        --region $AWS_REGION \
        --cli-input-json file:///dev/stdin \
        --query 'taskDefinition.taskDefinitionArn' \
        --output text)
    
    log_info "Task Definition 등록 완료: $TASK_DEF_ARN"
    
    # ECS 서비스 생성 또는 업데이트
    SERVICE_NAME="${PROJECT_NAME}-service"
    
    # 기존 서비스 확인
    if aws ecs describe-services \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $AWS_REGION \
        --query 'services[0].serviceName' \
        --output text | grep -q $SERVICE_NAME; then
        
        log_info "기존 서비스 업데이트 중..."
        aws ecs update-service \
            --cluster $CLUSTER_NAME \
            --service $SERVICE_NAME \
            --task-definition $TASK_DEF_ARN \
            --region $AWS_REGION > /dev/null
    else
        log_info "새 서비스 생성 중..."
        
        # 서브넷과 보안그룹 조회
        SUBNET_IDS=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $AWS_REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`SubnetIds`].OutputValue' \
            --output text)
        
        SECURITY_GROUP_ID=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $AWS_REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`SecurityGroupId`].OutputValue' \
            --output text)
        
        TARGET_GROUP_ARN=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $AWS_REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`TargetGroupArn`].OutputValue' \
            --output text)
        
        aws ecs create-service \
            --cluster $CLUSTER_NAME \
            --service-name $SERVICE_NAME \
            --task-definition $TASK_DEF_ARN \
            --desired-count 1 \
            --launch-type FARGATE \
            --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
            --load-balancers "targetGroupArn=$TARGET_GROUP_ARN,containerName=contract-analyzer,containerPort=8000" \
            --region $AWS_REGION > /dev/null
    fi
    
    log_success "ECS 서비스 배포 완료"
    
    # 서비스 안정화 대기
    log_info "서비스 안정화 대기 중... (최대 10분)"
    aws ecs wait services-stable \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $AWS_REGION
    
    log_success "서비스 안정화 완료"
else
    log_warning "서비스 배포를 건너뜁니다."
fi

# 배포 완료
echo ""
log_success "🎉 배포 완료!"
echo ""
echo "📍 서비스 정보:"
echo "   - ALB DNS: http://$ALB_DNS"
echo "   - ECS 클러스터: $CLUSTER_NAME"
echo "   - S3 버킷: $S3_BUCKET_NAME"
echo "   - 리전: $AWS_REGION"
echo ""
echo "🔧 관리 명령어:"
echo "   - 로그 확인: aws logs tail /ecs/lawro-contract-analyzer --follow --region $AWS_REGION"
echo "   - 서비스 상태: aws ecs describe-services --cluster $CLUSTER_NAME --services ${PROJECT_NAME}-service --region $AWS_REGION"
echo "   - 스택 삭제: aws cloudformation delete-stack --stack-name ${PROJECT_NAME}-infrastructure --region $AWS_REGION"
echo ""
echo "✅ LawRo Contract Analyzer가 AWS에서 실행 중입니다!" 