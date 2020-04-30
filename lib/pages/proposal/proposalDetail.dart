import 'package:cfapi/pages/widgets/span.dart';
import 'package:cfapi/services/score.dart';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class proposalDetail extends StatelessWidget {

  final Score score; 
  proposalDetail(this.score);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('成峰积分 － 奖扣详情',style:TextStyle(fontSize:16)),
        centerTitle: true,
        actions: [
          Row(
            children: <Widget>[
              FlatButton(
                onPressed: () async {
                  final storage = FlutterSecureStorage();
                  await storage.deleteAll();
                  Navigator.pushReplacementNamed(context, '/login');
                }, 
                child: Text('退出', style:TextStyle(color:Colors.white)),
              )
            ],
          ),
        ],
      ),
      body: Container(
        padding: EdgeInsets.all(8.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Row(
              children: <Widget>[
                Expanded(child: Span('提交：', score.pname)),              
                Expanded(child: Span('奖扣：','${score.classify} ${score.score}')),
                Expanded(child: Span('奖扣对象：', score.tname))
              ],
            ),
            Span('说明：', score.description),
            Span('审核意见：', score.commit),
            Span('复议：', score.appeal),
            Span('奖扣条款：', score.rule),
            Span('奖扣时间：', score.create_at),
            Span('审核进度：', score.state),
          ],
        )
      ),
    );
  }
}