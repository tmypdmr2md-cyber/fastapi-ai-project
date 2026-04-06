import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';


export class CopykitInfrustractureStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const apiLambda = new lambda.Function(this, 'CopykitApiLambda', {
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset("../app/"),
      handler: "copykit_api.handler",
    });
  }
}
