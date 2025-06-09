# LawRo Contract Analyzer - AWS 배포 가이드

## 🌐 AWS 배포 개요

이 프로젝트는 AWS ECS Fargate를 사용하여 컨테이너화된 애플리케이션을 완전 관리형으로 배포합니다.

### 🏗️ 아키텍처 구성

```
Internet → ALB → ECS Fargate Task
                    ├── ChatBot Container (Port 8000)
                    └── Contract Analyzer Container (Port 8000)
                         └── S3 Bucket (계약서 저장)
```

### 📦 AWS 리소스

- **ECS Fargate**: 컨테이너 실행 환경
- **Application Load Balancer**: 트래픽 분산
- **ECR**: Docker 이미지 저장소
- **S3**: 계약서 파일 저장
- **VPC**: 네트워크 격리
- **CloudWatch**: 로그 및 모니터링
- **IAM**: 권한 관리

## 🚀 빠른 배포

### 1. 사전 요구사항

```bash
# AWS CLI 설치 (v2 권장)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Docker 설치
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# AWS 인증 설정
aws configure
```

### 2. 배포 실행

```bash
# 실행 권한 부여
chmod +x aws/deploy.sh

# 전체 배포 (인프라 + 이미지 + 서비스)
./aws/deploy.sh \
    -a YOUR_AWS_ACCOUNT_ID \
    -k YOUR_UPSTAGE_API_KEY \
    -b your-unique-bucket-name

# 단계별 배포
./aws/deploy.sh -a 123456789012 -k up_xxxxx --skip-build  # 인프라만
./aws/deploy.sh -a 123456789012 -k up_xxxxx --skip-infra --skip-deploy  # 이미지만
./aws/deploy.sh -a 123456789012 -k up_xxxxx --skip-infra --skip-build  # 서비스만
```

### 3. 배포 확인

```bash
# 서비스 상태 확인
aws ecs describe-services \
    --cluster lawro-cluster \
    --services lawro-service \
    --region ap-northeast-2

# 로그 확인
aws logs tail /ecs/lawro-contract-analyzer --follow --region ap-northeast-2
```

## 📋 상세 설정

### 환경변수 설정

배포 스크립트는 다음 환경변수를 사용합니다:

```bash
# 필수 설정
AWS_ACCOUNT_ID=123456789012          # AWS 계정 ID
UPSTAGE_API_KEY=up_xxxxxxxxxxxxx     # Upstage API Key

# 선택적 설정
AWS_REGION=ap-northeast-2            # AWS 리전
PROJECT_NAME=lawro                   # 프로젝트 이름
S3_BUCKET_NAME=your-bucket-name      # S3 버킷 이름 (유니크해야 함)
ENVIRONMENT=production               # 배포 환경
```

### CloudFormation 파라미터

```yaml
Parameters:
  ProjectName: lawro                    # 리소스 이름 접두사
  Environment: production               # 환경 태그
  UpstageApiKey: up_xxxxx              # Upstage API Key
  S3BucketName: lawro-contracts-bucket # S3 버킷 이름
```

## 🔧 고급 설정

### 1. 리소스 사이징

#### CPU/Memory 조정
`aws/task-definition.json`에서 수정:

```json
{
  "cpu": "2048",        # 1024, 2048, 4096
  "memory": "4096",     # 2048, 4096, 8192
  "containerDefinitions": [
    {
      "name": "chatbot",
      "memory": 2048,     # 컨테이너별 메모리
      "cpu": 1024         # 컨테이너별 CPU
    }
  ]
}
```

#### Auto Scaling 설정

```bash
# Auto Scaling 타겟 등록
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/lawro-cluster/lawro-service \
    --min-capacity 1 \
    --max-capacity 10

# CPU 기반 스케일링 정책
aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/lawro-cluster/lawro-service \
    --policy-name cpu-scaling \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

### 2. 네트워크 설정

#### 사용자 정의 VPC 사용

```yaml
# CloudFormation 템플릿에서 기존 VPC ID 사용
Parameters:
  ExistingVpcId:
    Type: AWS::EC2::VPC::Id
    Description: 기존 VPC ID

Resources:
  # VPC 생성 대신 기존 VPC 참조
  # VPC: !Ref ExistingVpcId
```

#### 보안 그룹 커스터마이징

```yaml
ECSSecurityGroup:
  Type: AWS::EC2::SecurityGroup
  Properties:
    SecurityGroupIngress:
      - IpProtocol: tcp
        FromPort: 8000
        ToPort: 8000
        SourceSecurityGroupId: !Ref ALBSecurityGroup  # ALB에서만 접근 허용
```

### 3. 도메인 및 SSL 설정

#### Route 53 + ACM 설정

```bash
# SSL 인증서 발급
aws acm request-certificate \
    --domain-name api.yourdomain.com \
    --validation-method DNS \
    --region ap-northeast-2

# Route 53 레코드 생성
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890 \
    --change-batch file://dns-change.json
```

#### HTTPS 리스너 추가

```yaml
HTTPSListener:
  Type: AWS::ElasticLoadBalancingV2::Listener
  Properties:
    LoadBalancerArn: !Ref ApplicationLoadBalancer
    Port: 443
    Protocol: HTTPS
    Certificates:
      - CertificateArn: !Ref SSLCertificate
    DefaultActions:
      - Type: forward
        TargetGroupArn: !Ref TargetGroup
```

## 📊 모니터링 및 로깅

### CloudWatch 설정

```bash
# 커스텀 메트릭 생성
aws logs create-log-group \
    --log-group-name /ecs/lawro-custom \
    --region ap-northeast-2

# 알람 설정
aws cloudwatch put-metric-alarm \
    --alarm-name "LawRo-High-CPU" \
    --alarm-description "ECS CPU 사용률 80% 초과" \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold
```

### 로그 분석

```bash
# 실시간 로그 확인
aws logs tail /ecs/lawro-contract-analyzer --follow

# 특정 시간 범위 로그
aws logs filter-log-events \
    --log-group-name /ecs/lawro-contract-analyzer \
    --start-time 1640995200000 \
    --end-time 1641081600000

# 에러 로그 필터링
aws logs filter-log-events \
    --log-group-name /ecs/lawro-contract-analyzer \
    --filter-pattern "ERROR"
```

## 💰 비용 최적화

### Fargate Spot 사용

```yaml
ECSService:
  Type: AWS::ECS::Service
  Properties:
    CapacityProviderStrategy:
      - CapacityProvider: FARGATE_SPOT
        Weight: 70
      - CapacityProvider: FARGATE
        Weight: 30
```

### 예약 인스턴스

```bash
# Savings Plans 추천 확인
aws ce get-savings-plans-purchase-recommendation \
    --term-in-years ONE_YEAR \
    --payment-option PARTIAL_UPFRONT \
    --service-specification EC2InstanceFamily=m5
```

## 🛠️ 문제 해결

### 일반적인 문제

#### 1. Task 시작 실패

```bash
# Task 정의 확인
aws ecs describe-task-definition \
    --task-definition lawro-contract-analyzer

# Task 실패 이유 확인
aws ecs describe-tasks \
    --cluster lawro-cluster \
    --tasks TASK_ARN
```

#### 2. 이미지 Pull 실패

```bash
# ECR 로그인 확인
aws ecr get-login-password --region ap-northeast-2 | \
    docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 존재 확인
aws ecr describe-images \
    --repository-name lawro-contract-analyzer
```

#### 3. 네트워크 연결 문제

```bash
# 보안 그룹 규칙 확인
aws ec2 describe-security-groups \
    --group-ids sg-xxxxxxxx

# 서브넷 라우팅 확인
aws ec2 describe-route-tables \
    --filters "Name=association.subnet-id,Values=subnet-xxxxxxxx"
```

### 로그 분석 도구

```bash
# 성능 메트릭 조회
aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name CPUUtilization \
    --dimensions Name=ServiceName,Value=lawro-service \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-01T23:59:59Z \
    --period 3600 \
    --statistics Average
```

## 🔄 업데이트 및 롤백

### Blue/Green 배포

```bash
# 새 Task Definition 생성
aws ecs register-task-definition \
    --cli-input-json file://new-task-definition.json

# 서비스 업데이트
aws ecs update-service \
    --cluster lawro-cluster \
    --service lawro-service \
    --task-definition lawro-contract-analyzer:NEW_REVISION

# 롤백
aws ecs update-service \
    --cluster lawro-cluster \
    --service lawro-service \
    --task-definition lawro-contract-analyzer:PREVIOUS_REVISION
```

### 자동화된 배포

```bash
# 이미지만 업데이트
./aws/deploy.sh \
    -a 123456789012 \
    -k up_xxxxx \
    --skip-infra \
    --skip-deploy

# 서비스만 업데이트
./aws/deploy.sh \
    -a 123456789012 \
    -k up_xxxxx \
    --skip-infra \
    --skip-build
```

## 🗑️ 리소스 정리

### 전체 스택 삭제

```bash
# ECS 서비스 스케일 다운
aws ecs update-service \
    --cluster lawro-cluster \
    --service lawro-service \
    --desired-count 0

# 서비스 삭제
aws ecs delete-service \
    --cluster lawro-cluster \
    --service lawro-service

# CloudFormation 스택 삭제
aws cloudformation delete-stack \
    --stack-name lawro-infrastructure \
    --region ap-northeast-2

# ECR 이미지 삭제
aws ecr batch-delete-image \
    --repository-name lawro-contract-analyzer \
    --image-ids imageTag=latest

aws ecr batch-delete-image \
    --repository-name lawro-chatbot \
    --image-ids imageTag=latest
```

## 📞 지원 및 문의

### 유용한 명령어

```bash
# 전체 리소스 상태 확인
aws cloudformation describe-stacks \
    --stack-name lawro-infrastructure \
    --region ap-northeast-2

# 비용 확인
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost
```

### AWS 리소스 태그

모든 리소스는 다음 태그로 관리됩니다:

- `Project: lawro`
- `Environment: production`
- `ManagedBy: CloudFormation`

---

**참고**: 이 가이드는 AWS 환경에서의 운영 배포를 다룹니다. 로컬 개발은 `README_DOCKER.md`를 참조하세요. 