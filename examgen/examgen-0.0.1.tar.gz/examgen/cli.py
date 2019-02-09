import os
import click

try:
    from examgen.examgen import Exam, BatchGenerator
except ModuleNotFoundError:
    from examgen import Exam, BatchGenerator


@click.command()
@click.option("-e", "--exam", "exam", required=True, type=click.File())
@click.option("-rq", "--random-questions", "random_questions", is_flag=True)
@click.option("-ra", "--random-answers", "random_answers", is_flag=True)
@click.option("-b", "--batch", "batch", is_flag=True)
@click.option("-q", "--quantity", "quantity", type=int)
@click.option("-m", "--merge", "merge", is_flag=True)
@click.option("-fb", "--front-and-back", "front_and_back", is_flag=True)
def generate(exam, random_questions, random_answers, batch,
             quantity, merge, front_and_back):
    
    exam_path = os.path.abspath(exam.name)

    if batch:
        batch = BatchGenerator()

        if quantity is None:
            raise click.UsageError("You must define the quantity in the batch generation.")

        batch.generate(exam_path, quantity, random_answers=random_answers,
                       merge=merge, front_and_back=front_and_back)
    else:
        exam = Exam(exam_path, random_answers=random_answers,
                    random_questions=random_questions)
        exam.generate()
  

if __name__ == "__main__":
    generate()