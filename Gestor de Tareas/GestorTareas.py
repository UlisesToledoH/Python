import json
import os
import argparse

task_file = 'taks.json'

def load_taks():
    if not os.path.exists(task_file):
        return []
    with open(task_file,'r', encoding='utf-8') as file:
        return json.load(file)

def save_tasks(tasks):
    with open(task_file, 'w', encoding='utf-8') as file:
        json.dump(task_file,file,indent=2,ensure_ascii=False)

def add_taks(desc):
    tasks = load_taks()
    tasks.append({'desc' : desc, 'done' : False})
    save_tasks(tasks)
    print(f"\nTarea guardada exitosamente!")

def list_tasks():
    tasks = load_taks()
    if not tasks: 
        print("No hay tareas por mostrar")
        return 0
    for i,t in enumerate(tasks, 1):
        status = 'ok' if t['done'] else 'X'
        print(f"{i}. [{status}] {t['desc']}")
    
def mark_done(id):
    tasks = load_taks()
    try:
        tasks[id-1]['done'] = True
        save_tasks(tasks)
        print(f"{id}. Tarea completada!")
    except IndexError:
        print(f"No existe la tarea con ese ID")
    
def delete_task(id):
    tasks = load_taks()
    try:
        removed = tasks.pop(id-1)
        save_tasks(tasks)
        print(f"Tarea removida: {removed['desc']}")
    except IndexError:
        print("\nNo existe la tarea")
    
def main():
    parser = argparse.ArgumentParser(description="Gestor de tareas CLI")
    sub = parser.add_subparsers(dest='cmd', required=True)

    sub.add_parser('list', help='Listar todas las tareas')
    p_add = sub.add_parser('add', help='Agregar una nueva tarea')
    p_add.add_argument('desc', help='Descripción de la tarea')

    p_done = sub.add_parser('done', help='Marcar tarea como completada')
    p_done.add_argument('id', type=int, help='ID de la tarea a marcar')

    p_del = sub.add_parser('delete', help='Eliminar una tarea')
    p_del.add_argument('id', type=int, help='ID de la tarea a eliminar')

    args = parser.parse_args()
    if args.cmd == 'add':
        add_taks(args.desc)
    elif args.cmd == 'list':
        list_tasks()
    elif args.cmd == 'done':
        mark_done(args.id)
    elif args.cmd == 'delete':
        delete_task(args.id)
    
if __name__ == '__main__':
    main()