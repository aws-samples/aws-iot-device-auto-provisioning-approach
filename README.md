**Introduction**
============
This package will showcase a device automatic provision approach solution using AWS Lambda function and verifying the device using DynamoDB.

**How to Use**
============

1.Download this package from aws-samples (<https://github.com/aws-samples/aws-iot-device-auto-provisioning-approach.git>). Download AWS FreeRTOS source code (<https://github.com/aws/amazon-freertos.git>) and apply the patch:

``` bash
mkdir ~/environment
cd ~/environment
git clone https://github.com/aws-samples/aws-iot-device-auto-provisioning-approach.git
cd aws-iot-device-auto-provisioning-approach/amazon-freertos/
git clone https://github.com/aws/amazon-freertos.git
cd amazon-freertos/
git checkout 201906.00_Major -b auto-provisioning
git am ../0001-Add-IoT-Lab-Workshop-Device-Auto-Provision-sample-co.patch
```

2.Please reference the link (<https://iotlabtpe.github.io/iotlab_workshop/lab/lab-4.html>) to generate and register CA with AWS Command Line. For more information about AWS Command Line, please check the link(<https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html>).

3.Build code:

``` bash
cd vendors/espressif/boards/esp32/aws_demos/
make all -j4
```

4.Install the related python packages and pack the Lambda sample code:

``` bash
cd ~/environment/aws-iot-device-auto-provisioning-approach/lambda
pip install -t ./ -r requirements.txt
zip -r jitrSampleFunction.zip * .[^.]*
```

## License

This solution is licensed under the MIT-0 License. See the LICENSE file.