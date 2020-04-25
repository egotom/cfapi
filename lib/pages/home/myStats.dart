import 'package:cfapi/config/theme.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter/material.dart';
import 'package:charts_flutter/flutter.dart' as charts;
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
  List lst=[];
  @override
  void initState() {
    stats();
    super.initState();
  }

  stats() async{
    Map<String,dynamic> result= await http('get','stats');
    if(result['error']==0){
      setState(() {lst=result['lst'];});
    }
  }

  @override
  Widget build(BuildContext context) {
    var data = [
      TSS(DateTime(2020, 1, 10), 15),
      TSS(DateTime(2020, 2, 10), 20),
      TSS(DateTime(2020, 3, 10), 38),
      TSS(DateTime(2020, 4, 10), 50),
      TSS(DateTime(2020, 5, 10), 38),
      TSS(DateTime(2020, 6, 10), 48),
      TSS(DateTime(2020, 7, 10), 30),
      TSS(DateTime(2020, 8, 10), 35),
      TSS(DateTime(2020, 9, 10), 38),
      TSS(DateTime(2020, 10, 10), 50),
      TSS(DateTime(2020, 11, 10), 58),
      TSS(DateTime(2020, 12, 10), 40),
    ];

    var series = [
      charts.Series<TSS, DateTime>(
        id: 'Sales',
        colorFn: (_, __) => charts.MaterialPalette.blue.shadeDefault,
        domainFn: (TSS sales, _) => sales.time,
        measureFn: (TSS sales, _) => sales.sales,
        data: data,
      ),
    ];
  
    return SingleChildScrollView(      
      child: Column(
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
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
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
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
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
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
                              Text('--' ,style:MyTheme().scdf),
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