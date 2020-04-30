import 'package:cfapi/config/theme.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;
import 'package:intl/intl.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

class TSS {
  final DateTime time;
  final int sales;
  TSS(this.time, this.sales);
}

class MyStats extends StatefulWidget {
  @override
  _MyStatsState createState() => _MyStatsState();
}

class _MyStatsState extends State<MyStats> {
  bool loading =true;
  List<TSS> lst=[];
  List me=[['-','-','-'],['-','-','-'],['-','-','-']];
  @override
  void initState() {
    stats();
    super.initState();
  }

  stats() async{
    Map<String,dynamic> result= await http('get','stats');
    if(result['error']==0){
      List<TSS> data=[];
      for(var ri in result['lst']){
        DateTime tp=DateFormat("yyyy.MM").parse(ri[0]);
        data.add(TSS(tp,ri[1]));
      }
      setState(() {
        lst=data;
        me=result['me'];
        loading=false;
      });
    }    
  }

  @override
  Widget build(BuildContext context) {
    var series = [
      charts.Series<TSS, DateTime>(
        id: 'Sales',
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (TSS sales, _) => sales.time,
        measureFn: (TSS sales, _) => sales.sales,
        data: lst,
      ),
    ];
  
    return SingleChildScrollView(      
      child:(loading)? SpinKitCircle(color: Colors.blue,size: 70): Column(
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: Card(
                  color:MyTheme().scdc,
                  child: InkWell(
                    splashColor: Colors.white.withAlpha(80),
                    child: Container(
                      width: 100,
                      height: 100,
                      padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text('月积分: ' ,style:MyTheme().scdf),
                              Text('月排名: ' ,style:MyTheme().scdf),
                              Text('团队排名: ' ,style:MyTheme().scdf),
                            ],
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: <Widget>[
                              Text('${me[0][0]}' ,style:MyTheme().scdf),
                              Text('${me[0][1]}' ,style:MyTheme().scdf),
                              Text('${me[0][2]}' ,style:MyTheme().scdf),
                            ],
                          ),
                        ],
                      ),
                    ),
                  )
                ),
              ),
              Expanded(
                child: Card(
                  color:MyTheme().scdc,
                  child: InkWell(
                    splashColor: Colors.white.withAlpha(80),
                    child: Container(
                      width: 100,
                      height: 100,
                      padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text('年积分:' ,style:MyTheme().scdf),
                              Text('年排名:' ,style:MyTheme().scdf),
                              Text('团队排名:' ,style:MyTheme().scdf),
                            ],
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: <Widget>[
                              Text('${me[1][0]}' ,style:MyTheme().scdf),
                              Text('${me[1][1]}' ,style:MyTheme().scdf),
                              Text('${me[1][2]}' ,style:MyTheme().scdf),
                            ],
                          ),
                        ],
                      ),
                    ),
                  )
                ),
              ),
              Expanded(
                child: Card(
                  color:MyTheme().scdc,
                  child: InkWell(
                    splashColor: Colors.white.withAlpha(80),
                    child: Container(
                      width: 100,
                      height: 100,
                      padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text('累计积分:' ,style:MyTheme().scdf),
                              Text('累计排名:' ,style:MyTheme().scdf),
                              Text('团队排名:' ,style:MyTheme().scdf),
                            ],
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: <Widget>[
                              Text('${me[2][0]}' ,style:MyTheme().scdf),
                              Text('${me[2][1]}' ,style:MyTheme().scdf),
                              Text('${me[2][2]}' ,style:MyTheme().scdf),
                            ],
                          ),
                        ],
                      ),
                    ),
                  )
                ),
              ),
            ],
          ),
          
          SizedBox(height: 60),
          Text(''),
          SizedBox(height: 300,
            child: Padding(
              padding: EdgeInsets.all(8.0),
              child: charts.TimeSeriesChart(
                series, 
                animate: true,
                //primaryMeasureAxis: charts.NumericAxisSpec(
                //  tickFormatterSpec: charts.BasicNumericTickFormatterSpec.fromNumberFormat(
                //    NumberFormat.compactSimpleCurrency()
                //  )
                //),
                domainAxis: charts.DateTimeAxisSpec(
                  tickFormatterSpec: charts.AutoDateTimeTickFormatterSpec(
                    day: charts.TimeFormatterSpec(
                      format: 'd', 
                      transitionFormat: 'MM/dd/yy'
                    )
                  )
                )
              ),
            )
          ),
        ],
      ),
    );
  }
}