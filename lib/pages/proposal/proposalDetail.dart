import 'package:flutter/material.dart';

class proposalDetail extends StatelessWidget {

  final int id; 
  proposalDetail(this.id);

  @override
  Widget build(BuildContext context) {
    return Container(
      child:Text(id.toString())
    );
  }
}