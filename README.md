# XG-040G-MD PonWrt ˢ�������ֲ�

�������ֵ������ֲ᣺��¼���� �� ����ȫ��ԭ������ �� У�� �� Stock2UBI ���Ǩ�� �� pbs05 U-Boot �� PonWrt �� PON/WAN �� �滻���ա�

ÿ������������Ԥ�ڽ�����쳣�������ṩ 19 ������������ơ����ȵ���/�ָ��������͹���������

## �Ķ�

���زֿ� ZIP ����ѹ��˫�� `Open-Guide.cmd`������������� [docs/index.html](docs/index.html)������Ҫ��������npm ���������ļ��ƶ��������ǰ�ȵ������ȡ�

�ֿ���**�ֲἰ���ݸ����ű���Ŀ**����������ֱ��ˢ��Ĺ̼���Windows ������������ԭ�����ݻ�˽�����á��ֲ��е� `00-Open-Manual.cmd`��`03-Verify-Kit.cmd`��`08-Verify-Backup.cmd` ��Ŀ¼·�������������߹��߰�Լ�������Ǳ��ֿ������õĿ�ִ�й��߰���

�������׹��߰����� `docs/index.html` ���µ��ð� `manual/index.html` ʹ�ã���Ҫ�� HTML ���������̼���������δ׼�����߰����Ȱ� [�����嵥](docs/downloads.json) ����Դ���汾��SHA256 ���ֲ�·��׼���ļ���ϵͳ���������������鵵�ڣ���Ҫ��ѹȡ��ͨ MD UBI sysupgrade/recovery������ʹ�� MF/TF��USB-SFP ��ͬ������������

## ���÷�Χ

- ������ Nokia **XG-040G-MD UBI**�������� MF/TF��
- ���·����Ҫԭ�� root��ƥ��� AArch64/�ں˼� NAND ����������ǿ�к��԰汾��顣
- �ĵ�ʹ�� **2026-10-15 �̶���ʷ���**��PonWrt ����Ԥ���� a57faf9��pbs05 U-Boot v2026.07-4��Stock2UBI v0.1.14���������°汾�Ƽ���
- ������������ XG-PON��10G-EPON 10G/1G �Ѳ��ԣ�XGS-PON��10G-EPON 10G/10G δ���ԣ�GPON��EPON 1G/1G ��δʵ�֡������Ƶ����°汾��֧�������
- ˢд���޸����棻�ȱ��ݲ�У��ȫ��ԭ�������ͱ��� bosa/ri���ĵ�����֤ÿ̨ NAND������ OLT����֤��ȫ��ҵ����ݡ�

## ����������

[���ýṹʾ��](docs/example-settings.md) �������������ýṹ��[�հ׼�¼ģ��](docs/connection-record.example.txt) ֻ�������Լ��ı��ظ�������Ҫ�ύ��ʵ SN/LOID������ƾ�ݡ�WAN ��ַ��IPv6 ǰ׺��MAC���豸���кš�ԭ��ת������־��

���ݸ����ű�ֻ��ȡ�豸 MTD ��д����ʵ U �̣�����У�����������豸���ű�������� NAND ����������֤��Ƭ�ָ���

## ������У��

```sh
python src/build.py
python tests/check_project.py
node tests/navigation.cjs
```

Python 3 �� Node.js �����ڹ���/��飻�Ķ� HTML ����Ҫ��װ�������ļ��������˽��ȣ���������������ر��棬�����ļ���Ҫ�ύ�����Ը��ǵ���/�����߼����ı�һ���ԣ�δ����ʵ�ʹ�è��ÿ����������������ա�

## ����������

- [PonWrt](https://github.com/pbs05/ponwrt)
- [Stock2UBI](https://github.com/pbs05/an758x-stock2ubi)
- [pbs05 U-Boot](https://github.com/pbs05/uboot-an758x)
- [PON ����](https://github.com/pbs05/openwrt-pon-drivers)
- [PON �û�̬](https://github.com/pbs05/openwrt-pon-userspace)
- [ԭ�����ʲο�](https://openwrt.org/toh/nokia/xg-040g-md)

���ֿ�ԭ���ֲᡢҳ�����͸����ű����� MIT���� [LICENSE](LICENSE)��������Ŀ�����ߺ͹̼�������ѭ��ԭʼ���ɣ����ֿⲻ������Ȩ��Щ���
