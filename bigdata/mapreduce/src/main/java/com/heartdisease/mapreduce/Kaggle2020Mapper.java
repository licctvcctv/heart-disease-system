package com.heartdisease.mapreduce;

import java.io.IOException;
import java.util.List;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class Kaggle2020Mapper extends Mapper<LongWritable, Text, NullWritable, Text> {
    private final Text output = new Text();

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString();
        if (line.startsWith("HeartDisease,")) {
            return;
        }
        List<String> row = CsvRecordParser.parse(line);
        if (row.size() < 18) {
            return;
        }

        output.set(MapperSupport.tsv(
            "kaggle_2020",
            MapperSupport.yesNo(MapperSupport.value(row, 0)),
            MapperSupport.value(row, 9),
            MapperSupport.sexCode(MapperSupport.value(row, 8)),
            MapperSupport.numeric(row, 1),
            MapperSupport.intNumeric(row, 5),
            MapperSupport.intNumeric(row, 6),
            MapperSupport.yesNo(MapperSupport.value(row, 2)),
            MapperSupport.yesNo(MapperSupport.value(row, 3)),
            MapperSupport.yesNo(MapperSupport.value(row, 12)),
            MapperSupport.numeric(row, 14),
            MapperSupport.yesNo(MapperSupport.value(row, 4)),
            MapperSupport.diabetesFlag(MapperSupport.value(row, 11)),
            MapperSupport.yesNo(MapperSupport.value(row, 16)),
            MapperSupport.yesNo(MapperSupport.value(row, 15)),
            MapperSupport.yesNo(MapperSupport.value(row, 17)),
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE
        ));
        context.write(NullWritable.get(), output);
    }
}
